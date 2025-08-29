###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from abc import ABC, abstractmethod
from krausening.logging import LogManager

import json
from typing import Optional


class AuthAdapterBase(ABC):
    """
    Check if the user is allowed to perform the action on the resource
    """

    logger = LogManager.get_instance().get_logger("AuthzAdapterBase")

    @abstractmethod
    def _authorize_impl(
        self, user: dict, resource: str, action: str, role: Optional[str] = None
    ) -> bool:
        pass

    def authorize(
        self,
        user: dict,
        resource: str,
        action: str,
        user_ip: str,
        request_url: str,
        role: Optional[str] = None,
    ) -> bool:
        self.log_authorize(
            user=user,
            resource=resource,
            action=action,
            user_ip=user_ip,
            request_url=request_url,
            role=role,
        )

        pdp_decision = self._authorize_impl(
            user=user,
            resource=resource,
            action=action,
            role=role,
        )

        self.log_pdp_decision(user, pdp_decision)

        return pdp_decision

    def log_pdp_decision(self, user: str, pdp_decision):
        permit_or_deny = "PERMIT" if pdp_decision else "DENY"

        self.logger.info(f"PDP decision for user: {user}, was {permit_or_deny}")

    def log_authorize(
        self,
        user: dict,
        resource: str,
        action: str,
        user_ip: str,
        request_url: str,
        role: Optional[str] = None,
    ):
        authz_log_info = {
            "user": user,
            "resource": resource,
            "action": action,
            "role": role,
            "ip": user_ip,
            "request_url": request_url,
        }

        self.logger.info("Authorization start")

        self.logger.info("Auth request info:\n" + json.dumps(authz_log_info, indent=2))
