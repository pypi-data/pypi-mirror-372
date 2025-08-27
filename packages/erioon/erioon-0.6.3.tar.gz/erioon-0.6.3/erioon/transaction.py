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

import uuid
from erioon.functions import get_index_data, create_msgpack_file, calculate_shard_number, async_log, update_index_file_insert

class Transaction:
    def __init__(self, user_id_cont, database, collection, container_url):
        self.user_id_cont = user_id_cont
        self.database = database
        self.collection = collection
        self.container_url = container_url
        self.staged_records = []

    def insert_one(self, record):
        if "_id" not in record or not record["_id"]:
            record["_id"] = str(uuid.uuid4())
        self.staged_records.append(record)

    def commit(self):
        # Check duplicates for all staged records
        index_data = get_index_data(self.user_id_cont, self.database, self.collection, self.container_url)
        existing_ids = set()
        for shard in index_data:
            for ids in shard.values():
                existing_ids.update(ids)

        # Assign new IDs if duplicates found
        for record in self.staged_records:
            if record["_id"] in existing_ids:
                new_id = str(uuid.uuid4())
                record["_id"] = new_id

        # Write all records to shard files
        for record in self.staged_records:
            create_msgpack_file(self.user_id_cont, self.database, self.collection, record, self.container_url)
            shard_number = calculate_shard_number(self.user_id_cont, self.database, self.collection, self.container_url)
            update_index_file_insert(self.user_id_cont, self.database, self.collection, record["_id"], shard_number, self.container_url)

        async_log(self.user_id_cont, self.database, self.collection, "POST", "SUCCESS", f"{len(self.staged_records)} records inserted atomically", len(self.staged_records), self.container_url)

        self.staged_records.clear()

    def rollback(self):
        self.staged_records.clear()
        async_log(self.user_id_cont, self.database, self.collection, "POST", "ERROR", "Transaction rollback: no records inserted", 0, self.container_url)
