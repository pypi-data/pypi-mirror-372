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

import json
from urllib.parse import urlparse
from erioon.read import handle_get_all, handle_find_one, handle_find_many, handle_count_records
from erioon.create import handle_insert_one, handle_insert_many
from erioon.delete import handle_delete_one, handle_delete_many
from erioon.update import handle_update_one, handle_update_many, handle_replace_one
from erioon.ping import handle_connection_ping

class Collection:
    def __init__(
        self,
        user_id,
        db_id,
        coll_id,
        metadata,
        database,
        cluster,
        sas_url,
    ):
        """
        Initialize a Collection object that wraps Erioon collection access.

        Args:
            user_id (str): The authenticated user's ID.
            db_id (str): The database ID.
            coll_id (str): The collection ID.
            metadata (dict): Metadata info about this collection (e.g., schema, indexing, etc.).
            database (str): Name or ID of the database.
            cluster (str): Cluster name or ID hosting the database.
            sas_url (str): Full SAS URL used to access the storage container.
        """
        self.user_id = user_id
        self.db_id = db_id
        self.coll_id = coll_id
        self.metadata = metadata
        self.database = database
        self.cluster = cluster

        parsed_url = urlparse(sas_url.rstrip("/"))
        container_name = parsed_url.path.lstrip("/").split("/")[0]
        account_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        sas_token = parsed_url.query
        self.container_url = f"{account_url}/{container_name}?{sas_token}"

    # PRINT ERIOON 
    def _print_loading(self):
        """Prints a loading message (likely for UX in CLI or SDK usage)."""
        print("Erioon is loading...")

    # CHECK READ / WRITE LICENCE
    def _is_read_only(self):
        """Check if the current database is marked as read-only."""
        return self.database == "read"

    # RESPONSE FOR ONLY WRITE
    def _read_only_response(self):
        """Standardized error response for blocked write operations."""
        return "[Erioon Error - Database access denied] This user is not allowed to perform write operations in the selected collection."

    # GET ALL RECORDS OF A COLLECTION
    def get_all(self, limit=1000000):
        """
        Fetch all records from the collection (up to a limit).
        """
        self._print_loading()
        result, status_code = handle_get_all(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            limit=limit,
            container_url=self.container_url,
        )
        return result

    # FINDS A SPECIFIC RECORD OF A COLLECTION
    def find_one(self, filters: dict | None = None):
        """
        Fetch a single record that matches specific key-value filters.
        """
        if self._is_read_only():
            return self._read_only_response()

        if filters is None:
            filters = {}

        search_criteria = [{k: v} for k, v in filters.items()]

        result, status_code = handle_find_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            search_criteria=search_criteria,
            container_url=self.container_url,
        )
        return result
    
    # FINDS MULTIPLE RECORDS OF A COLLECTION
    def find_many(self, filters: dict | None = None, limit: int = 1000):
        """
        Fetch multiple records that match specific key-value filters.

        Args:
            filters (dict): Filters to match records.
            limit (int): Maximum number of records to return (default: 1000).

        Returns:
            dict: Result from `handle_find_many()`
        """
        if self._is_read_only():
            return self._read_only_response()

        self._print_loading()

        if filters is None:
            filters = {}

        if limit > 500_000:
            raise ValueError("Limit of 500,000 exceeded")

        search_criteria = [{k: v} for k, v in filters.items()]

        result, status_code = handle_find_many(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            search_criteria=search_criteria,
            limit=limit,
            container_url=self.container_url,
        )
        return result

    # INSERT A SINGLE RECORD IN A COLLECTION
    def insert_one(self, record):
        """
        Insert a single record into the collection.
        """
        if self._is_read_only():
            return self._read_only_response()
        response, status = handle_insert_one(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            record=record,
            container_url=self.container_url,
        )
        if status == 200:
            print("Insertion was successful.")
        else:
            print(f"Error inserting record: {response}")
        return response, status

    # INSERT MULTIPLE RECORDS INTO A COLLECTION
    def insert_many(self, data):
        """
        Insert multiple records into the collection.

        Args:
            data (list): List of record dicts.

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        response, status = handle_insert_many(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            data=data,
            container_url=self.container_url,
        )
        if status == 200:
            print("Insertion of multiple records was successful.")
        else:
            print(f"Error inserting records: {response}")
        return response, status

    # DELETE A SINGLE RECORD BASED ON _ID OR KEY
    def delete_one(self, record_to_delete):
        """
        Delete a single record based on its _id or nested key.
        """
        if self._is_read_only():
            return self._read_only_response()
        response, status = handle_delete_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            data_to_delete=record_to_delete,
            container_url=self.container_url,
        )
        if status == 200:
            print("Deletion was successful.")
        else:
            print(f"Error deleting record: {response}")
        return response, status

    # DELETE MANY RECORDS IN BATCHES
    def delete_many(self, records_to_delete_list, batch_size=10):
        """
        Delete multiple records in batches.
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        response, status = handle_delete_many(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            data_to_delete_list=records_to_delete_list,
            batch_size=batch_size,
            container_url=self.container_url,
        )
        if status == 200:
            print("Batch deletion was successful.")
        else:
            print(f"Error deleting records: {response}")
        return response, status

    # UPDATE A RECORD
    def update_one(self, filter_query: dict, update_query: dict):
        """
        Update a record in-place by filtering and applying update logic.
        """
        if self._is_read_only():
            return self._read_only_response()
        response, status = handle_update_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            filter_query=filter_query,
            update_query=update_query,
            container_url=self.container_url,
        )
        if status == 200:
            print("Update was successful.")
        else:
            print(f"Error updating record: {response}")
        return response, status

    # UPDATE MULTIPLE RECORDS
    def update_many(self, update_tasks: list):
        """
        Update multiple records in-place by applying a list of filter + update operations.

        Each item in `update_tasks` should be a dict:
            {
                "filter": { ... },
                "update": {
                    "$set": {...}, "$push": {...}, "$remove": [...]
                }
            }

        Returns:
            (dict, int): Summary response and HTTP status code.
        """
        if self._is_read_only():
            return self._read_only_response()
        self._print_loading()
        
        response, status = handle_update_many(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            update_tasks=update_tasks,
            container_url=self.container_url,
        )

        if status == 200:
            print(f"Successfully updated {response.get('success')}")
        else:
            print(f"Error updating records: {response}")

        return response, status

    # REPLACE A SINGLE RECORDS BASED ON THE FILTER QUERY
    def replace_one(self, filter_query: dict, replacement: dict):
        """
        Replaces a single record matching `filter_query` with the full `replacement` document.

        - If `_id` is **not** in the replacement, preserves the original `_id`.
        - If `_id` **is** in the replacement, uses the new `_id`.

        Args:
            filter_query (dict): Must contain a single key-value pair.
            replacement (dict): New record to replace the old one.

        Returns:
            (dict, int): Response message and HTTP status code.
        """
        if self._is_read_only():
            return self._read_only_response()

        response, status = handle_replace_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            filter_query=filter_query,
            replacement=replacement,
            container_url=self.container_url,
        )

        if status == 200:
            print("Replacement was successful.")
        else:
            print(f"Error replacing record: {response}")

        return response, status

    # PING AND CHECK CONNECTION
    def ping(self):
        """
        Health check / ping to verify collection accessibility.
        """
        self._print_loading()
        response, status = handle_connection_ping(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            container_url=self.container_url,
        )
        if status == 200:
            print("Connection ping successful.")
        else:
            print(f"Ping failed: {response}")
        return response, status

    # COUNT ALL THE RECORDS
    def count_records(self) -> int:
        """
        Count the total number of documents in the collection (across all shards).

        Returns:
            int: Total document count.
        """
        if self._is_read_only():
            return 0
        self._print_loading()

        count, status = handle_count_records(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            container_url=self.container_url,
        )
        return count
    
    # INSERT ONE VECTOR
    def vector_insert_one(self, record: dict):
        """
        Insert a single vector-based record into the collection.

        Required format:
            {
                "id" or "_id": str,
                "vector": List[float],
                "metadata": Optional[dict]
            }

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()

        # Validate record structure
        if not isinstance(record, dict):
            return {"error": "Record must be a dictionary."}, 400

        if "vector" not in record:
            return {"error": "Missing 'vector' field."}, 400

        if not isinstance(record["vector"], list) or not all(isinstance(x, (int, float)) for x in record["vector"]):
            return {"error": "'vector' must be a list of floats."}, 400

        # Directly call handle_insert_one
        response, status = handle_insert_one(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            record=record,
            container_url=self.container_url,
        )

        if status == 200:
            print("Vector insertion was successful.")
        else:
            print(f"Error inserting vector record: {response}")

        return response, status
    
    # INSERT MANY VECTORS
    def vector_insert_many(self, records: list):
        """
        Insert multiple vector-based records into the collection.

        Each record should follow the format:
            {
                "id" or "_id": str,
                "vector": List[float],
                "metadata": Optional[dict]
            }

        Returns:
            tuple: (response message, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()

        self._print_loading()

        if not isinstance(records, list):
            return {"error": "Records must be a list of dictionaries."}, 400

        validated_records = []
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                return {"error": f"Record at index {i} is not a dictionary."}, 400

            if "vector" not in record:
                return {"error": f"Missing 'vector' in record at index {i}."}, 400

            if not isinstance(record["vector"], list) or not all(isinstance(x, (int, float)) for x in record["vector"]):
                return {"error": f"'vector' must be a list of floats at index {i}."}, 400

            # Normalize 'id' to '_id'
            if "id" in record and "_id" not in record:
                record["_id"] = record.pop("id")

            validated_records.append(record)

        response, status = handle_insert_many(
            user_id_cont=self.user_id,
            database=self.db_id,
            collection=self.coll_id,
            data=validated_records,
            container_url=self.container_url,
        )

        if status == 200:
            print("Vector batch insertion was successful.")
        else:
            print(f"Error inserting vector records: {response}")

        return response, status

    # FIND A VECTOR RECORD BY ID
    def vector_find_by_id(self, _id: str):
        """
        Retrieve a vector record by its ID ("_id" or "id").
    
        Args:
            _id (str): The identifier of the vector record.
    
        Returns:
            tuple: (record, HTTP status code)
        """
        if self._is_read_only():
            return self._read_only_response()
    
        if not _id or not isinstance(_id, str):
            return None

        search_criteria = [{"_id": _id}]
        response, status = handle_find_one(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=self.coll_id,
            search_criteria=search_criteria,
            container_url=self.container_url,
        )

        if status != 200 or not response or "record" not in response:
            search_criteria = [{"id": _id}]
            response, status = handle_find_one(
                user_id=self.user_id,
                db_id=self.db_id,
                coll_id=self.coll_id,
                search_criteria=search_criteria,
                container_url=self.container_url,
            )

        if status != 200 or not response or "record" not in response:
            return None

        record = response["record"]

        if "vector" not in record:
            return None

        return record


    def __str__(self):
        """Pretty print the collection metadata."""
        return json.dumps(self.metadata, indent=4)

    def __repr__(self):
        """Simplified representation for debugging or introspection."""
        return f"<Collection coll_id={self.coll_id}>"
