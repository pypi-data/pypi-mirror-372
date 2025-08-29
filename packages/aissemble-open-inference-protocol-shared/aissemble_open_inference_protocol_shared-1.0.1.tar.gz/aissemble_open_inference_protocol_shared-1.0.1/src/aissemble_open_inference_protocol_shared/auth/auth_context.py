###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from dataclasses import dataclass


@dataclass
class AuthContext:
    authz_adapter: object
    bearer_token: str
    auth_action: str
    auth_resource: str
    user_ip: str
    request_url: str
