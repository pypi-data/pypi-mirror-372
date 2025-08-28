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
from io import BytesIO
import uuid
import datetime

def record_matches_filter(record, filter_dict):
    '''
    Checks if a record (a dict) matches a filter (also a dict).
    Supports nested keys using dot notation (e.g., "address.city").
    '''
    def get_nested_value(d, key_path):
        keys = key_path.split('.')
        val = d
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return None
        return val

    for key, expected_value in filter_dict.items():
        actual_value = get_nested_value(record, key)
        if actual_value != expected_value:
            return False
    return True


def handle_delete_one(user_id, db_id, coll_id, data_to_delete, container_url):
    '''
    Deletes a single record from a specific collection in Azure Blob Storage.
    Record can be matched by `_id` or using a filter.
    
    Logs the operation to `logs.msgpack` and updates the corresponding shard file and index.
    '''
    try:
        container_client = ContainerClient.from_container_url(container_url)
        index_filename = f"{db_id}/{coll_id}/index.msgpack"
        logs_filename = f"{db_id}/{coll_id}/logs.msgpack"

        index_blob_client = container_client.get_blob_client(index_filename)
        try:
            index_data = msgpack.unpackb(index_blob_client.download_blob().readall(), raw=False)
        except Exception:
            return {"status": "KO", "message": "Failed to load index data."}, 500

        if "_id" in data_to_delete:
            target_id = data_to_delete["_id"]
            shard_key = None
            for sk, id_list in index_data.items():
                if target_id in id_list:
                    shard_key = sk
                    break
            if not shard_key:
                return {"status": "KO", "message": f"Record with _id {target_id} not found."}, 404
            shard_keys_to_check = [shard_key]
        else:
            shard_keys_to_check = list(index_data.keys())

        matched_record = None
        matched_shard_key = None
        shard_blob_clients = {}

        for shard_key in shard_keys_to_check:
            shard_filename = f"{db_id}/{coll_id}/{shard_key}.msgpack"
            if shard_key not in shard_blob_clients:
                shard_blob_clients[shard_key] = container_client.get_blob_client(shard_filename)
            shard_blob_client = shard_blob_clients[shard_key]

            try:
                shard_records = msgpack.unpackb(shard_blob_client.download_blob().readall(), raw=False)
            except Exception:
                continue

            for rec in shard_records:
                if "_id" in data_to_delete and rec.get("_id") == data_to_delete["_id"]:
                    matched_record = rec
                    matched_shard_key = shard_key
                    break
                elif record_matches_filter(rec, data_to_delete):
                    matched_record = rec
                    matched_shard_key = shard_key
                    break

            if matched_record:
                break

        if not matched_record:
            return {"status": "KO", "message": "Record not found matching the filter."}, 404

        new_shard_records = [rec for rec in shard_records if rec.get("_id") != matched_record["_id"]]

        with BytesIO() as buf:
            buf.write(msgpack.packb(new_shard_records, use_bin_type=True))
            buf.seek(0)
            shard_blob_clients[matched_shard_key].upload_blob(buf, overwrite=True)

        if matched_record["_id"] in index_data.get(matched_shard_key, []):
            index_data[matched_shard_key].remove(matched_record["_id"])

        with BytesIO() as buf:
            buf.write(msgpack.packb(index_data, use_bin_type=True))
            buf.seek(0)
            index_blob_client.upload_blob(buf, overwrite=True)

        logs_blob_client = container_client.get_blob_client(logs_filename)
        try:
            logs_data = msgpack.unpackb(logs_blob_client.download_blob().readall(), raw=False)
        except Exception:
            logs_data = {}

        log_id = str(uuid.uuid4())
        logs_data[log_id] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "method": "DELETE",
            "type": "SUCCESS",
            "log": f"Deleted record with _id {matched_record['_id']} from {coll_id}.",
            "count": 1,
        }

        with BytesIO() as buf:
            buf.write(msgpack.packb(logs_data, use_bin_type=True))
            buf.seek(0)
            logs_blob_client.upload_blob(buf, overwrite=True)

        return {
            "status": "OK",
            "message": f"Record with _id {matched_record['_id']} deleted successfully.",
            "deleted_id": matched_record["_id"]
        }, 200

    except Exception as e:
        return {
            "status": "KO",
            "message": "An error occurred during deletion.",
            "error": str(e)
        }, 500


def handle_delete_many(user_id, db_id, coll_id, data_to_delete_list, batch_size, container_url):
    '''
    Deletes multiple records in batch from a collection.
    Accepts a list of dicts which may include `_id` or filter fields.

    Updates shard files, index, and logs each operation to `logs.msgpack`.
    '''
    try:
        container_client = ContainerClient.from_container_url(container_url)

        index_filename = f"{db_id}/{coll_id}/index.msgpack"
        logs_filename = f"{db_id}/{coll_id}/logs.msgpack"

        blob_client = container_client.get_blob_client(index_filename)
        try:
            index_data = msgpack.unpackb(blob_client.download_blob().readall(), raw=False)
        except Exception:
            return {"status": "KO", "message": "Failed to load index data."}, 500

        logs_blob_client = container_client.get_blob_client(logs_filename)
        try:
            logs_data = msgpack.unpackb(logs_blob_client.download_blob().readall(), raw=False)
        except Exception:
            logs_data = {}

        id_to_shard = {}
        for sk, id_list in index_data.items():
            for _id in id_list:
                id_to_shard[_id] = sk

        results = []

        def process_batch(batch):
            shard_to_ids = {}
            filters_needing_scan = []

            for filter_criteria in batch:
                _id = filter_criteria.get("_id")
                if _id:
                    shard_key = id_to_shard.get(_id)
                    if not shard_key:
                        results.append({"_id": _id, "status": "KO", "message": "Record not found"})
                    else:
                        shard_to_ids.setdefault(shard_key, []).append(_id)
                else:
                    filters_needing_scan.append(filter_criteria)

            if filters_needing_scan:
                for shard_key in index_data.keys():
                    shard_filename = f"{db_id}/{coll_id}/{shard_key}.msgpack"
                    shard_blob_client = container_client.get_blob_client(shard_filename)

                    try:
                        shard_records = msgpack.unpackb(shard_blob_client.download_blob().readall(), raw=False)
                    except Exception:
                        for filt in filters_needing_scan:
                            results.append({"_id": filt.get("_id", None), "status": "KO", "message": "Failed to load shard"})
                        continue

                    for filt in filters_needing_scan:
                        matched_ids = [rec["_id"] for rec in shard_records if record_matches_filter(rec, filt)]
                        if matched_ids:
                            shard_to_ids.setdefault(shard_key, []).extend(matched_ids)

                for shard_key in shard_to_ids:
                    shard_to_ids[shard_key] = list(set(shard_to_ids[shard_key]))

                matched_ids_all = set()
                for ids in shard_to_ids.values():
                    matched_ids_all.update(ids)

                for filt in filters_needing_scan:
                    if not any(record_matches_filter({'_id': _id}, filt) for _id in matched_ids_all):
                        results.append({"_id": filt.get("_id", None), "status": "KO", "message": "Record not found"})

            for shard_key, ids_to_delete in shard_to_ids.items():
                shard_filename = f"{db_id}/{coll_id}/{shard_key}.msgpack"
                shard_blob_client = container_client.get_blob_client(shard_filename)

                try:
                    shard_records = msgpack.unpackb(shard_blob_client.download_blob().readall(), raw=False)
                except Exception:
                    for _id in ids_to_delete:
                        results.append({"_id": _id, "status": "KO", "message": "Failed to load shard"})
                    continue

                original_len = len(shard_records)
                new_shard_records = [rec for rec in shard_records if rec.get("_id") not in ids_to_delete]

                if len(new_shard_records) == original_len:
                    for _id in ids_to_delete:
                        results.append({"_id": _id, "status": "KO", "message": "Record not found in shard"})
                    continue

                with BytesIO() as buf:
                    buf.write(msgpack.packb(new_shard_records, use_bin_type=True))
                    buf.seek(0)
                    shard_blob_client.upload_blob(buf, overwrite=True)

                for _id in ids_to_delete:
                    if _id in index_data.get(shard_key, []):
                        index_data[shard_key].remove(_id)
                        results.append({"_id": _id, "status": "OK", "message": "Deleted successfully"})
                    else:
                        results.append({"_id": _id, "status": "KO", "message": "Record missing in index"})

        for i in range(0, len(data_to_delete_list), batch_size):
            batch = data_to_delete_list[i : i + batch_size]
            process_batch(batch)

        with BytesIO() as buf:
            buf.write(msgpack.packb(index_data, use_bin_type=True))
            buf.seek(0)
            blob_client.upload_blob(buf, overwrite=True)

        log_id = str(uuid.uuid4())
        logs_data[log_id] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "method": "DELETE",
            "type": "SUCCESS",
            "log": f"Deleted {len(data_to_delete_list)} records from {coll_id} in batches of {batch_size}.",
            "count": len(data_to_delete_list),
        }

        with BytesIO() as buf:
            buf.write(msgpack.packb(logs_data, use_bin_type=True))
            buf.seek(0)
            logs_blob_client.upload_blob(buf, overwrite=True)

        return {"status": "OK", "results": results}, 200

    except Exception as e:
        return {"status": "KO", "message": "Error during batch deletion", "error": str(e)}, 500
