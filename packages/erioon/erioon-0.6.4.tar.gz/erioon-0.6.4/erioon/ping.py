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

from erioon.functions import async_log
from azure.storage.blob import ContainerClient

# PING CONNECTION VERIFICATION
def handle_connection_ping(user_id, db_id, coll_id, container_url):
    """
    Checks if a specific collection exists within an storage container 
    and logs the status of the connection attempt asynchronously.

    Parameters:
    - user_id (str): Identifier of the user making the request.
    - db_id (str): Database identifier (used as a folder prefix).
    - coll_id (str): Collection identifier (used as a folder prefix).
    - container_url: Container SAS URL.

    Returns:
    - tuple(dict, int): A tuple containing a status dictionary and an HTTP status code.
        - If collection is found, returns status "OK" and HTTP 200.
        - If collection is missing, returns status "KO" with HTTP 404.
        - On any exception, returns status "KO" with HTTP 500.
    """
    try:
        container_client = ContainerClient.from_container_url(container_url)
        directory_path = f"{db_id}/{coll_id}/"

        blobs = container_client.list_blobs(name_starts_with=directory_path)
        blob_names = [blob.name for blob in blobs]

        if not blob_names:
            async_log(user_id, db_id, coll_id, "PING", "ERROR", f"No collection {coll_id} found.", 1, container_url)
            return {"status": "KO", "error": f"No collection {coll_id} found."}, 404

        async_log(user_id, db_id, coll_id, "PING", "SUCCESS", "Connection successful", 1, container_url)
        return {"status": "OK", "message": "Connection successful"}, 200

    except Exception as e:
        async_log(user_id, db_id, coll_id, "PING", "ERROR", f"Connection failed: {str(e)}", 1, container_url)
        return {"status": "KO", "error": "Connection failed", "message": str(e)}, 500
