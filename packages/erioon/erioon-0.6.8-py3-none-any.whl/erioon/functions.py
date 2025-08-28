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
import uuid
from io import BytesIO
import datetime
from threading import Thread
import random
import string

# CREATE BLOB CONTAINER
def create_container_if_not_exists(container_name, container_url):
    """
    Checks if the storage container exists; if not, creates it.
    
    Args:
        container_name: Name of the container to check/create.
        container_url: Container SAS URL.
    """
    container_client = ContainerClient.from_container_url(container_url)
    if not container_client.exists():
        container_client.create_container()

# GET SHARD FILENAME
def get_shard_file_name(user_id_cont, database, collection, container_url, next_shard_number=False):
    """
    Determines the filename of the current (or next) shard MessagePack file for writing data.
    
    The filename format is: {database}/{collection}/{collection}_{shard_number}.msgpack

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        container_url: Container SAS URL.
        next_shard_number: If True, returns filename for the next shard (increment shard number).

    Returns:
        Filename string of the shard to be used.
    """
    container_client = ContainerClient.from_container_url(container_url)
    
    base_shard_name = f"{database}/{collection}/{collection}"
    
    files = container_client.list_blobs(name_starts_with=base_shard_name)
    existing_shards = [int(blob.name.split('_')[-1].split('.')[0]) for blob in files if blob.name.endswith('.msgpack')]
    
    if existing_shards:
        next_shard = max(existing_shards) + 1 if next_shard_number else max(existing_shards)
    else:
        next_shard = 1

    return f"{base_shard_name}_{next_shard}.msgpack"

# GET SHARD LIMIT
def get_shard_limit(user_id_cont, database, collection, container_url):
    """
    Retrieves the maximum number of records allowed in a single shard from the
    collection_settings.msgpack file, or returns a default limit if file doesn't exist.

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        container_url: Container SAS URL.

    Returns:
        Integer shard limit (default 100000).
    """
    container_client = ContainerClient.from_container_url(container_url)
    config_blob_client = container_client.get_blob_client(blob=f"{database}/{collection}/collection_settings.msgpack")
    
    if not config_blob_client.exists():
        return 100000
    
    try:
        raw = config_blob_client.download_blob().readall()
        config_data = msgpack.unpackb(raw, raw=False)
    except Exception:
        return 100000

    return config_data.get("shard_limit", 100000)

# CREATE MSGPACK FILE
def create_msgpack_file(user_id_cont, database, collection, data, container_url):
    """
    Writes the given record data into the appropriate MessagePack shard file.
    Automatically manages shard rollover based on shard size limit.

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        data: The record data dict to store.
        container_url: Container SAS URL.

    Returns:
        The filename of the shard where the record was stored.
    """
    container_client = ContainerClient.from_container_url(container_url)
    
    msgpack_filename = get_shard_file_name(user_id_cont, database, collection, container_url)

    msgpack_blob_client = container_client.get_blob_client(blob=msgpack_filename)

    existing_records = []
    max_records_per_shard = get_shard_limit(user_id_cont, database, collection, container_url)

    if msgpack_blob_client.exists():
        with BytesIO(msgpack_blob_client.download_blob().readall()) as existing_file:
            existing_records = msgpack.unpackb(existing_file.read(), raw=False)

    if len(existing_records) >= max_records_per_shard:
        msgpack_filename = get_shard_file_name(user_id_cont, database, collection, container_url, next_shard_number=True)
        msgpack_blob_client = container_client.get_blob_client(blob=msgpack_filename)
        existing_records = []  

    existing_records.append(data)

    with BytesIO() as out_file:
        out_file.write(msgpack.packb(existing_records, use_bin_type=True))
        out_file.seek(0)
        msgpack_blob_client.upload_blob(out_file, overwrite=True)

    return msgpack_filename

# GET INDEX OF DOCUMENTS
def get_index_data(user_id_cont, database, collection, container_url):
    """
    Retrieves the content of the index.msgpack file that tracks which records are stored in which shards.

    Args:
        user_id_cont: User identifier or context.
        database: Database name.
        collection: Collection name.
        container_url: Container SAS URL.

    Returns:
        List of shard mappings (list of dicts) or empty list if file not found or error.
    """
    container_client = ContainerClient.from_container_url(container_url)
    index_blob_client = container_client.get_blob_client(blob=f"{database}/{collection}/index.msgpack")

    try:
        raw_data = index_blob_client.download_blob().readall()
        return msgpack.unpackb(raw_data, raw=False) if raw_data else []
    except Exception:
        return []

# CHECK DUPLICATE IDs
def is_duplicate_id(user_id_cont, database, collection, _id, container_url):
    """
    Checks if the given record _id is already present in the index.msgpack across shards.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        _id: Record ID to check.
        container_url: Container SAS URL.

    Returns:
        True if _id exists in any shard, else False.
    """
    index_data = get_index_data(user_id_cont, database, collection, container_url)

    for shard in index_data:
        for shard_name, ids in shard.items():
            if _id in ids:
                return True 
    return False

# OPS COUNTER
def update_ops_counter(database, collection, count, container_client):
    """
    Updates the operation count for the current UTC day in ops.msgpack.
    """
    from datetime import datetime

    today = datetime.utcnow().date().isoformat()
    ops_path = f"{database}/{collection}/ops.msgpack"
    blob_client = container_client.get_blob_client(ops_path)

    try:
        existing_blob = blob_client.download_blob().readall()
        ops_data = msgpack.unpackb(existing_blob, raw=False)
    except Exception:
        ops_data = {}

    ops_data[today] = ops_data.get(today, 0) + count

    with BytesIO() as buf:
        buf.write(msgpack.packb(ops_data, use_bin_type=True))
        buf.seek(0)
        blob_client.upload_blob(buf, overwrite=True)

# SAVE LOGS
def save_logs(user_id_cont, database, collection, method, log_type, log_message, count, container_url):
    container_client = ContainerClient.from_container_url(container_url)
    blob_path = f"{database}/{collection}/logs.msgpack"
    logs_blob_client = container_client.get_blob_client(blob=blob_path)

    try:
        existing_blob = logs_blob_client.download_blob().readall()
        logs_data = msgpack.unpackb(existing_blob, raw=False)
    except Exception:
        logs_data = {}

    log_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    logs_data[log_id] = {
        "timestamp": timestamp,
        "method": method.upper(),
        "type": log_type.upper(),
        "log": log_message,
    }

    sorted_logs = sorted(logs_data.items(), key=lambda item: item[1]["timestamp"], reverse=True)
    trimmed_logs = dict(sorted_logs[:150])

    with BytesIO() as out_file:
        out_file.write(msgpack.packb(trimmed_logs, use_bin_type=True))
        out_file.seek(0)
        logs_blob_client.upload_blob(out_file, overwrite=True)

    update_ops_counter(database, collection, count, container_client)

# ASYNC LOG SAVING
def async_log(user_id, db, collection, method, status, message, count, container_url):
    """
    Executes the save_logs function asynchronously in a separate thread,
    allowing non-blocking log operations.

    Args:
        user_id: User identifier/context.
        db: Database name.
        collection: Collection name.
        method: Operation method.
        status: Log status (SUCCESS, ERROR, etc.).
        message: Log message or data.
        count: Number of affected records.
        container_url: Container SAS URL.
    """
    Thread(target=save_logs, args=(user_id, db, collection, method, status, message, count, container_url)).start()

# GENERATE UNIQUE ID KEY
def generate_unique_id(existing_ids):
    """
    Generates a new UUID string that does not collide with any IDs in existing_ids.

    Args:
        existing_ids: Iterable of already existing _id strings.

    Returns:
        Unique UUID string not in existing_ids.
    """
    while True:
        new_id = str(uuid.uuid4()) 
        if new_id not in existing_ids:
            return new_id

# UPDATE INDEX DURING INSERT
def update_index_file_insert(user_id_cont, database, collection, record_id, shard_number, container_url):
    """
    Updates index.msgpack to register a newly inserted record_id under the appropriate shard.

    The index.msgpack structure is a list of dicts mapping shard names to list of record IDs:
    [
        { "collection_1": ["id1", "id2", ...] },
        { "collection_2": ["id3", "id4", ...] }
    ]

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        record_id: The _id of the inserted record.
        shard_number: The shard number where the record was stored.
        container_url: Container SAS URL.

    Returns:
        The record_id inserted.
    """
    container_client = ContainerClient.from_container_url(container_url)
    index_blob_client = container_client.get_blob_client(blob=f"{database}/{collection}/index.msgpack")

    index_data = []

    if index_blob_client.exists():
        try:
            raw_data = index_blob_client.download_blob().readall()
            index_data = msgpack.unpackb(raw_data, raw=False)
        except Exception:
            index_data = []

    shard_key = f"{collection}_{shard_number}"
    shard_found = False

    for shard in index_data:
        if shard_key in shard:
            shard[shard_key].append(record_id)
            shard_found = True
            break

    if not shard_found:
        index_data.append({shard_key: [record_id]})

    with BytesIO() as out_file:
        out_file.write(msgpack.packb(index_data, use_bin_type=True))
        out_file.seek(0)
        index_blob_client.upload_blob(out_file, overwrite=True)

    return record_id

# UPDATE INDEX FILE DURING DELETING
def update_index_file_delete(user_id_cont, database, collection, record_id, shard_number, container_url):
    """
    Removes a record_id from the index.msgpack under the correct shard upon deletion.

    Cleans up empty shard entries after removal.

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        record_id: The _id of the deleted record.
        shard_number: The shard number from which to remove the record.
        container_url: Container SAS URL.

    Returns:
        The record_id deleted.
    """
    container_client = ContainerClient.from_container_url(container_url)
    index_blob_client = container_client.get_blob_client(blob=f"{database}/{collection}/index.msgpack")

    index_data = []

    if index_blob_client.exists():
        try:
            raw_data = index_blob_client.download_blob().readall()
            index_data = msgpack.unpackb(raw_data, raw=False)
        except Exception:
            index_data = []

    shard_key = f"{collection}_{shard_number}"

    for shard in index_data:
        if shard_key in shard:
            if record_id in shard[shard_key]:
                shard[shard_key].remove(record_id)
                if not shard[shard_key]:
                    index_data.remove(shard)
            break

    with BytesIO() as out_file:
        out_file.write(msgpack.packb(index_data, use_bin_type=True))
        out_file.seek(0)
        index_blob_client.upload_blob(out_file, overwrite=True)

    return record_id

# CALCULATE SHARD RECORDS
def calculate_shard_number(user_id_cont, database, collection, container_url):
    """
    Determines the shard number for storing a new record.

    Logic:
    - Lists existing shard files in the collection directory.
    - Extracts shard numbers from filenames.
    - Returns the highest shard number found, or 1 if none found.

    Args:
        user_id_cont: User identifier/context.
        database: Database name.
        collection: Collection name.
        container_url: Container SAS URL.

    Returns:
        Integer shard number to use.
    """
    container_client = ContainerClient.from_container_url(container_url)
    
    directory_path = f"{database}/{collection}/"
    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    
    shard_numbers = []
    for blob in blob_list:
        try:
            parts = blob.name.split("_")
            if blob.name.endswith(".msgpack"):
                num = int(parts[1].split(".")[0])
                shard_numbers.append(num)
        except Exception:
            continue 
    if shard_numbers:
        next_shard = max(shard_numbers)
    else:
        next_shard = 1
    return next_shard

# CHECK NESTED KEYS
def check_nested_key(data, key_path, value):
    """
    Recursively checks whether a nested key in a dictionary or list of dictionaries
    matches the specified value.

    Args:
        data (dict or list): The data structure (dict or list of dicts) to search.
        key_path (str): Dot-separated path to the nested key (e.g. "a.b.c").
        value: The value to compare against.

    Returns:
        bool: True if the key exists at the nested path and equals the value, else False.
    """
    keys = key_path.split('.') 
    
    if not keys:
        return False
    
    current_key = keys[0]
    remaining_keys = keys[1:]

    if isinstance(data, dict):
        if current_key in data:
            if not remaining_keys:
                if data[current_key] == value:
                    return True
            else:
                return check_nested_key(data[current_key], '.'.join(remaining_keys), value)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                if check_nested_key(item, '.'.join(remaining_keys), value):
                    return True
    return False


def encode_datetime_to_hex(dt):
    """
    Encode datetime to a fixed length hex string representing milliseconds since epoch.
    """
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    delta = dt - epoch
    millis = int(delta.total_seconds() * 1000)
    # Format to 12 hex chars (enough until year 10889)
    return f"{millis:012x}"

def decode_datetime_from_hex(hex_str):
    """
    Decode fixed length hex string back to datetime.
    """
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    millis = int(hex_str, 16)
    return epoch + datetime.timedelta(milliseconds=millis)

def generate_random_prefix(length=10):
    """
    Generate a random alphanumeric string of given length.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_next_id(last_id, shard_number):
    """
    last_id format: <datetime_hex>-<shard_hex>-<record_hex>
    unique identifier: 10 chars
    datetime_hex: 12 chars
    shard_hex: 2 chars
    record_hex: 6 chars
    """
    if not last_id:
        now = datetime.datetime.utcnow()
        record_num = 1
    else:
        try:
            datetime_hex, shard_hex, record_hex = last_id.split("-")
            last_record_num = int(record_hex, 16)
            record_num = last_record_num + 1
            now = datetime.datetime.utcnow()
        except Exception:
            now = datetime.datetime.utcnow()
            record_num = 1
            
    random_prefix = generate_random_prefix()
    datetime_hex = encode_datetime_to_hex(now)
    shard_hex = f"{shard_number:08x}"
    record_hex = f"{record_num:06x}"

    return f"{random_prefix}-{datetime_hex}-{shard_hex}-{record_hex}"
