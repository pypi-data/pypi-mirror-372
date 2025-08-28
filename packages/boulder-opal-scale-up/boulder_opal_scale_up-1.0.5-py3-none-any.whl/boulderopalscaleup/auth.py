# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from qctrlclient import ApiKeyAuth
from qctrlclient.defaults import (
    get_default_api_url,
)
from qctrlclient.exceptions import GraphQLQueryError


def get_default_api_key_auth(api_key: str) -> ApiKeyAuth:
    """
    Return a token-based authentication handler
    pointed to the default API URL.
    """
    auth = ApiKeyAuth(get_default_api_url(), api_key)

    # Check the API key.
    # We can thus infer that the API key is invalid if the access token cannot be fetched.
    try:
        _ = auth.access_token
    except GraphQLQueryError as error:
        raise RuntimeError(
            f"Invalid API key ({api_key}). Please check your key "
            "or visit https://accounts.q-ctrl.com to generate a new one.",
        ) from error

    return auth
