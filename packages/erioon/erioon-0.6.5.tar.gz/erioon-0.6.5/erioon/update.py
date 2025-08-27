# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK

import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import async_log

# UPDATE ONE RECORD
def handle_update_one(user_id, db_id, coll_id, filter_query, update_query, container_url):
    """
    Updates a single record in a collection based on a filter condition,
    applying one of the supported update operations, and logs the result asynchronously.

    Supported operations in `update_query`:
    - "$set": Overwrites the value at the specified (possibly nested) key.
    - "$push": Appends a value to a list at the specified key, or initializes the list if it doesn't exist.
    - "$remove": Deletes the specified key from the record.

    Parameters:
    - user_id (str): Identifier of the user making the update request.
    - db_id (str): Database identifier (used as a directory prefix).
    - coll_id (str): Collection identifier (used as a subdirectory under the database).
    - filter_query (dict): Key-value pairs that must match exactly in the record for it to be updated.
    - update_query (dict): Update operations to apply, using one of the supported operators ($set, $push, $remove).
    - container_url: Container SAS URL.

    Returns:
    - tuple(dict, int): A tuple containing:
        - A dictionary with either:
            - "success": Confirmation message if update succeeded.
            - "error": Error message if update failed.
        - HTTP status code:
            - 200 if a matching record is updated successfully.
            - 404 if no collections or matching records are found.
            - No 500s are explicitly returned; internal exceptions are silently caught.
    """
    container_client = ContainerClient.from_container_url(container_url)
    directory_path = f"{db_id}/{coll_id}/"

    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "PATCH_UPDT", "ERROR",
                  f"No collections found for the database {db_id}", 1, container_url)
        return {"error": f"No collections found for the database {db_id}"}, 404

    updated = False

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()

            if not msgpack_data:
                continue

            data_records = msgpack.unpackb(msgpack_data, raw=False)
            modified_records = []
            local_updated = False

            for record in data_records:
                if not updated:
                    match_found = all(record.get(k) == v for k, v in filter_query.items())
                    if match_found:
                        for op, changes in update_query.items():
                            if op == "$set":
                                for key, new_value in changes.items():
                                    keys = key.split(".")
                                    nested_obj = record
                                    for k in keys[:-1]:
                                        nested_obj = nested_obj.setdefault(k, {})
                                    nested_obj[keys[-1]] = new_value

                            elif op == "$push":
                                for key, new_value in changes.items():
                                    keys = key.split(".")
                                    nested_obj = record
                                    for k in keys[:-1]:
                                        nested_obj = nested_obj.setdefault(k, {})
                                    last_key = keys[-1]
                                    if last_key not in nested_obj:
                                        nested_obj[last_key] = [new_value]
                                    elif isinstance(nested_obj[last_key], list):
                                        nested_obj[last_key].append(new_value)
                                    else:
                                        nested_obj[last_key] = [nested_obj[last_key], new_value]

                            elif op == "$remove":
                                for key in changes:
                                    keys = key.split(".")
                                    nested_obj = record
                                    for k in keys[:-1]:
                                        nested_obj = nested_obj.get(k, {})
                                    last_key = keys[-1]
                                    if isinstance(nested_obj, dict) and last_key in nested_obj:
                                        del nested_obj[last_key]

                        updated = True
                        local_updated = True

                modified_records.append(record)

            if local_updated:
                packed_data = msgpack.packb(modified_records, use_bin_type=True)
                blob_client.upload_blob(packed_data, overwrite=True)
                async_log(user_id, db_id, coll_id, "PATCH_UPDT", "SUCCESS",
                          "Record updated successfully", len(modified_records), container_url)
                return {"success": "Record updated successfully"}, 200

        except Exception:
            continue

    if not updated:
        async_log(user_id, db_id, coll_id, "PATCH_UPDT", "ERROR",
                  "No matching record found", 1, container_url)
        return {"error": "No matching record found"}, 404

# UPDATE MULTIPLE RECORDS
def handle_update_many(user_id, db_id, coll_id, update_tasks, container_url):
    """
    Perform multiple record updates based on a list of filter-and-update tasks.

    Each task specifies a filter to match records and an update query to apply (using "$set", "$push", "$remove").
    The function applies updates across alls collection and aggregates results per task.
    For each task, it tracks how many records were updated and logs successes asynchronously.

    Args:
        user_id (str): The user ID performing the update.
        db_id (str): Database identifier.
        coll_id (str): Collection identifier.
        update_tasks (list[dict]): List of update tasks, each with:
            - "filter": dict specifying key-value pairs to match.
            - "update": dict with update operations.
        container_url: Container SAS URL.

    Returns:
        tuple(dict, int): A tuple containing:
            - Response dictionary summarizing:
                - Total number of updated records across all tasks.
                - Detailed results per task (updated count or errors).
            - HTTP status code:
                - 200 if one or more records updated.
                - 404 if no records were updated.
    """
    
    container_client = ContainerClient.from_container_url(container_url)
    directory_path = f"{db_id}/{coll_id}/"
    blob_list = list(container_client.list_blobs(name_starts_with=directory_path))
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    if not blob_names:
        return {"error": f"No collections found under {directory_path}"}, 404

    total_updates = 0
    task_results = []

    for task in update_tasks:
        filter_query = task.get("filter", {})
        update_query = task.get("update", {})
        updated_count = 0

        for blob_name in blob_names:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                msgpack_data = blob_client.download_blob().readall()

                if not msgpack_data:
                    continue

                records = msgpack.unpackb(msgpack_data, raw=False)
                modified = False

                for record in records:
                    if all(record.get(k) == v for k, v in filter_query.items()):
                        for op, changes in update_query.items():
                            if op == "$set":
                                for key, new_value in changes.items():
                                    nested = record
                                    keys = key.split(".")
                                    for k in keys[:-1]:
                                        nested = nested.setdefault(k, {})
                                    nested[keys[-1]] = new_value

                            elif op == "$push":
                                for key, value in changes.items():
                                    nested = record
                                    keys = key.split(".")
                                    for k in keys[:-1]:
                                        nested = nested.setdefault(k, {})
                                    last_key = keys[-1]
                                    if last_key not in nested:
                                        nested[last_key] = [value]
                                    elif isinstance(nested[last_key], list):
                                        nested[last_key].append(value)
                                    else:
                                        nested[last_key] = [nested[last_key], value]

                            elif op == "$remove":
                                for key in changes:
                                    nested = record
                                    keys = key.split(".")
                                    for k in keys[:-1]:
                                        nested = nested.get(k, {})
                                    last_key = keys[-1]
                                    if isinstance(nested, dict) and last_key in nested:
                                        del nested[last_key]

                        modified = True
                        updated_count += 1

                if modified:
                    packed_data = msgpack.packb(records, use_bin_type=True)
                    blob_client.upload_blob(packed_data, overwrite=True)

            except Exception as e:
                task_results.append({
                    "filter": filter_query,
                    "error": str(e)
                })
                continue

        if updated_count > 0:
            async_log(user_id, db_id, coll_id, "PATCH_UPDT_MANY", "SUCCESS",
                      f"Updated {updated_count} records", updated_count, container_url)
            task_results.append({
                "filter": filter_query,
                "updated": updated_count
            })
            total_updates += updated_count
        else:
            task_results.append({
                "filter": filter_query,
                "updated": 0,
                "error": "No matching records found"
            })

    if total_updates == 0:
        return {"error": "No records updated", "details": task_results}, 404
    return {"success": f"{total_updates} records updated", "details": task_results}, 200

# REPLACE ONE RECORD
def handle_replace_one(user_id, db_id, coll_id, filter_query, replacement, container_url):
    """
    Replace a single record identified by a single-field filter in a MsgPack collection.

    This function searches collection under `{db_id}/{coll_id}/` for a record matching the single filter field.
    Upon finding the record, it replaces the entire record with the provided `replacement` dictionary.
    If `replacement` lacks the `_id` field, the original record’s `_id` is preserved.
    Only one field is allowed in `filter_query`.

    Args:
        user_id (str): User ID performing the replacement.
        db_id (str): Database identifier.
        coll_id (str): Collection identifier.
        filter_query (dict): Dictionary with exactly one key-value pair to match.
        replacement (dict): New record to replace the matched one.
        container_url: Container SAS URL.
    Returns:
        tuple(dict, int): A tuple containing:
            - Response dictionary with:
                - "success": Confirmation message if replacement succeeded.
                - "error": Error message if no matching record was found or filter invalid.
            - HTTP status code:
                - 200 if replacement succeeded.
                - 400 if filter_query is invalid.
                - 404 if no matching record was found.
    """
    
    container_client = ContainerClient.from_container_url(container_url)
    directory_path = f"{db_id}/{coll_id}/"
    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [b.name for b in blob_list if b.name.endswith(".msgpack")]

    if len(filter_query) != 1:
        return {"error": "filter_query must contain exactly one field"}, 400

    filter_key, filter_value = list(filter_query.items())[0]

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob().readall()
            records = msgpack.unpackb(blob_data, raw=False)
            modified = False

            for i, record in enumerate(records):
                if record.get(filter_key) == filter_value:
                    original_id = record.get("_id")
                    new_record = replacement.copy()
                    if "_id" not in new_record:
                        new_record["_id"] = original_id
                    records[i] = new_record
                    modified = True
                    break

            if modified:
                packed = msgpack.packb(records, use_bin_type=True)
                blob_client.upload_blob(packed, overwrite=True)
                async_log(user_id, db_id, coll_id, "REPLACE", "SUCCESS",
                          "Record replaced successfully", 1, container_url)
                return {"success": "Record replaced successfully"}, 200

        except Exception as e:
            continue

    async_log(user_id, db_id, coll_id, "REPLACE", "ERROR",
              "No matching record found", 1, container_url)
    return {"error": "No matching record found"}, 404
