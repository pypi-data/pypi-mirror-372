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

from erioon.client import ErioonClient

def Auth(credential_string):
    """
    Authenticates a user using a colon-separated email:password string.

    Parameters:
    - credential_string (str): A string in the format "email:password"

    Returns:
    - ErioonClient instance: An instance representing the authenticated user.
      If authentication fails, the instance will contain the error message.

    Example usage:
    >>> from erioon.auth import Auth
    >>> client = Auth("<API_KEY>:<EMAIL>:<PASSWORD>")
    >>> print(client)  # prints user_id if successful or error message if not
    """
    return ErioonClient(credential_string)
