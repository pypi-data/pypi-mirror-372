import uuid
import datetime
from io import BytesIO
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import (
    calculate_shard_number,
    get_shard_limit
)

class InMemoryInsertOne:
    """
    InMemoryInsertOne class manages inserting single records efficiently into a sharded collection stored on storage.

    Key features:
    - Initializes by loading existing shard data, index, logs, and ops counter from blobs.
    - Preloads existing record IDs into memory for fast duplicate detection.
    - Manages shards based on a shard size limit, flushing full shards to blob storage.
    - Keeps an in-memory index mapping record IDs to shards, and flushes it to blob storage.
    - Buffers insertions and flushes data, index, logs, and ops counter when a threshold is reached or explicitly called.
    - Uses msgpack for efficient binary serialization of shard data.
    - Logs insertion operations with timestamps and metadata for auditing.
    - Automatically handles shard rollover when the current shard exceeds the size limit.

    Intended usage:
    - Create an instance per user/database/collection/container combination.
    - Use add_record(record) to insert a new record; duplicates will raise an error.
    - Periodically call flush_all() to persist data, logs, and counters.
    """
    def __init__(self, user_id, db, collection, container_url, flush_threshold=1):
        self.user_id = user_id
        self.db = db
        self.collection = collection
        self.container_url = container_url
        self.container_client = ContainerClient.from_container_url(container_url)

        self.shard_number = calculate_shard_number(user_id, db, collection, container_url)
        self.shard_filename = self._get_shard_filename(self.shard_number)
        self.index_filename = f"{db}/{collection}/index.msgpack"
        self.logs_filename = f"{db}/{collection}/logs.msgpack"
        self.ops_filename = f"{db}/{collection}/ops.msgpack"

        self.shard_records = self._load_blob(self.shard_filename, default=[])
        self.index_data = self._load_blob(self.index_filename, default={})
        self.logs_data = self._load_blob(self.logs_filename, default={})
        self.ops_data = self._load_blob(self.ops_filename, default={})

        self.shard_limit = get_shard_limit(user_id, db, collection, container_url)
        self.insert_count_since_flush = 0
        self.flush_threshold = flush_threshold

        self.existing_ids = set()
        self._populate_existing_ids()

        self.ops_accumulated_count = 0

    def _get_shard_filename(self, shard_num):
        return f"{self.db}/{self.collection}/{self.collection}_{shard_num}.msgpack"

    def _load_blob(self, filename, default):
        try:
            blob = self.container_client.get_blob_client(filename)
            return msgpack.unpackb(blob.download_blob().readall(), raw=False)
        except Exception:
            return default

    def get_last_inserted_id(self):
        if self.index_data:
            last_shard = f"{self.collection}_{self.shard_number}"
            ids = self.index_data.get(last_shard, [])
            if ids:
                return ids[-1]
        return None

    def add_log(self, method, log_type, log_message, count):
        log_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        self.logs_data[log_id] = {
            "timestamp": timestamp,
            "method": method.upper(),
            "type": log_type.upper(),
            "log": log_message,
        }

        if len(self.logs_data) > 150:
            sorted_logs = sorted(
                self.logs_data.items(),
                key=lambda item: item[1]["timestamp"],
                reverse=True
            )
            self.logs_data = {k: v for k, v in sorted_logs[:150]}

        self.ops_accumulated_count += count

    def _flush_ops_if_needed(self, force=False):
        if force or self.ops_accumulated_count >= 100:
            today = datetime.datetime.utcnow().date().isoformat()
            self.ops_data[today] = self.ops_data.get(today, 0) + self.ops_accumulated_count
            self.ops_accumulated_count = 0
            self.flush_ops()

    def flush_ops(self):
        self._flush_blob(self.ops_filename, self.ops_data)

    def _populate_existing_ids(self):
        self.existing_ids = set()
        for id_list in self.index_data.values():
            self.existing_ids.update(id_list)

    def add_record(self, record, force_flush=False):
        rec_id = record["_id"]

        if rec_id in self.existing_ids:
            raise ValueError(f"Duplicate _id detected: {rec_id}")
        self.existing_ids.add(rec_id)

        if len(self.shard_records) >= self.shard_limit:
            self.flush_shard()
            self.shard_number += 1
            self.shard_filename = self._get_shard_filename(self.shard_number)
            self.shard_records = []

        self.shard_records.append(record)

        shard_key = f"{self.collection}_{self.shard_number}"
        self.index_data.setdefault(shard_key, []).append(rec_id)

        self.insert_count_since_flush += 1

        if force_flush or self.insert_count_since_flush >= self.flush_threshold:
            self.flush_all()
            self.insert_count_since_flush = 0

    def flush_all(self):
        self.flush_shard()
        self.flush_index()
        self.flush_logs()
        self._flush_ops_if_needed(force=True)

    def flush_shard(self):
        self._flush_blob(self.shard_filename, self.shard_records)

    def flush_index(self):
        self._flush_blob(self.index_filename, self.index_data)

    def flush_logs(self):
        self._flush_blob(self.logs_filename, self.logs_data)

    def _flush_blob(self, filename, data):
        blob = self.container_client.get_blob_client(filename)
        with BytesIO() as buf:
            buf.write(msgpack.packb(data, use_bin_type=True))
            buf.seek(0)
            blob.upload_blob(buf, overwrite=True)
