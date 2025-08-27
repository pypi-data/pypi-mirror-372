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
from erioon.collection import Collection

class Database:
    def __init__(self, user_id, metadata, database=None, cluster=None, sas_url=None):
        """
        Initialize a Database instance.

        Args:
            user_id (str): The ID of the authenticated user.
            metadata (dict): Metadata containing information about the database and its collections.
            database (str, optional): The name or identifier of the database.
            cluster (str, optional): The cluster where the database is hosted.
            sas_url (str, optional): SAS URL for accessing storage container.
        """
        self.user_id = user_id
        self.metadata = metadata
        self.db_id = metadata.get("database_info", {}).get("_id")
        self.database = database
        self.cluster = cluster
        self.sas_url = sas_url

    def __getitem__(self, collection_id):
        """
        Enables dictionary-like access to collections within the database.

        Args:
            collection_id (str): Identifier of the collection to retrieve.

        Returns:
            Collection: An instance of the Collection class initialized with metadata.
            str: Error message if the collection is not found.
        """
        collections = self.metadata.get("database_info", {}).get("collections", {})
        coll_meta = collections.get(collection_id)

        if not coll_meta:
            return "No collection found"

        return Collection(
            user_id=self.user_id,
            db_id=self.db_id,
            coll_id=collection_id,
            metadata=coll_meta,
            database=self.database,
            cluster=self.cluster,
            sas_url=self.sas_url
        )

    def __str__(self):
        """
        Returns a nicely formatted JSON string of the database metadata.
        Useful for debugging and inspecting the database info.

        Returns:
            str: Pretty-printed JSON metadata.
        """
        return json.dumps(self.metadata, indent=4)

    def __repr__(self):
        """
        Returns a concise, informative string representation of the Database instance.

        Returns:
            str: Formatted string showing the database ID, cluster, and database name.
        """
        return f"<Database db_id={self.db_id}, cluster={self.cluster}, database={self.database}>"
