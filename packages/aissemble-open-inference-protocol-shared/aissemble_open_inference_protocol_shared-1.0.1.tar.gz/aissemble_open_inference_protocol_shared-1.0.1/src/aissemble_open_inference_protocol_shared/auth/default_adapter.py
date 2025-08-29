###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from .auth_adapter_base import AuthAdapterBase
from typing import Optional


class DefaultAdapter(AuthAdapterBase):
    def __init__(self):
        # This is just an example property that is not actually used.
        # A full implementation will make use of a service url.
        self.service_url = "http://localhost:<some port>/<some path>"

    def _authorize_impl(
        self, user: dict, resource: str, action: str, role: Optional[str] = None
    ) -> bool:
        return True
