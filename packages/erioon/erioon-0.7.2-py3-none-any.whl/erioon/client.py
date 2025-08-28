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

import requests
from datetime import datetime
from erioon.database import Database
from erioon.playbox import Playbox

class ErioonClient:
    def __init__(self, credential_string, base_url="https://sdk.erioon.com"):
        self.credential_string = credential_string
        self.base_url = base_url
        self.user_id = None
        self.login_metadata = None
        self.sas_tokens = {}

        parts = credential_string.split(":")

        if len(parts) == 1 and credential_string.startswith("erioon"):
            self.api = credential_string
            self.email = None
            self.password = None
        elif len(parts) == 2:
            self.email, self.password = parts
            self.api = None
        else:
            raise ValueError("Invalid credential format. Use 'erioon-xxxxx' or 'email:password'")

        try:
            self._perform_login()
        except Exception as e:
            print(f"[ErioonClient] Initialization error: {e}")

    def _perform_login(self):
        url = f"{self.base_url}/login_sdk"
        payload = {"api_key": self.api, "email": self.email, "password": self.password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.login_metadata = data
            self._update_metadata_fields()
        else:
            try:
                msg = response.json().get("error", "Login failed")
            except Exception:
                msg = response.text
            raise RuntimeError(f"[ErioonClient] Login failed: {msg}")

    def _update_metadata_fields(self):
        self.user_id = self.login_metadata.get("_id")
        self.cluster = self.login_metadata.get("cluster")
        self.database = self.login_metadata.get("database")

        self.sas_tokens = {}
        for db_id, sas_info in self.login_metadata.get("sas_tokens", {}).items():
            expiry_str = sas_info.get("expiry")
            expiry_dt = datetime.fromisoformat(expiry_str)
            self.sas_tokens[db_id] = {
                "expiry": expiry_dt,
                "sas_token": sas_info["sas_token"],
                "container_url": sas_info["container_url"],
                "storage_account": sas_info["storage_account"],
                "container": sas_info["container"],
            }

    def __getitem__(self, item_id):
        if not self.user_id:
            raise ValueError("Client not authenticated. Cannot access database.")

        return self._get_item_info(item_id)

    def _get_item_info(self, item_id):
        if item_id.startswith("db"):
            return self._get_standard_database_info(item_id)
        elif item_id.startswith("play"):
            return self._get_playbox_info(item_id)
        else:
            raise ValueError(f"Unknown prefix for '{item_id}'")

    def _get_standard_database_info(self, db_id):
        payload = {"user_id": self.user_id, "db_id": db_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/db_info", json=payload, headers=headers)

        if response.status_code == 200:
            db_info = response.json()
            sas_info = self.sas_tokens.get(db_id)
            if not sas_info:
                raise Exception(f"No login certificate token info for database id {db_id}")

            container_url = sas_info.get("container_url")
            sas_token = sas_info.get("sas_token")
            if not container_url or not sas_token:
                raise Exception("Missing login URL components")

            if not sas_token.startswith("?"):
                sas_token = "?" + sas_token
            sas_url = container_url.split("?")[0] + sas_token

            return Database(
                user_id=self.user_id,
                metadata=db_info,
                database=self.database,
                cluster= self.cluster,
                sas_url=sas_url
            )
        else:
            try:
                error_msg = response.json().get("error", response.text)
            except Exception:
                error_msg = response.text
            raise Exception(f"Failed to fetch database info: {error_msg}")

    def _get_playbox_info(self, playbox_id):
        url = f"{self.base_url}/playbox_info"
        payload = {"user_id": self.user_id, "playbox_id": playbox_id}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch playbox info: {response.text}")

        data = response.json()
        kubeconfig = data.get("kubeconfig")
        namespace = self.user_id
        sa_name = f"sa-{self.user_id}"
        cluster=self.cluster


        return Playbox(namespace, sa_name, kubeconfig, playbox_id, cluster)

    def __str__(self):
        return self.user_id if self.user_id else "[ErioonClient] Unauthenticated"

    def __repr__(self):
        return f"<ErioonClient user_id={self.user_id}>" if self.user_id else "<ErioonClient unauthenticated>"
