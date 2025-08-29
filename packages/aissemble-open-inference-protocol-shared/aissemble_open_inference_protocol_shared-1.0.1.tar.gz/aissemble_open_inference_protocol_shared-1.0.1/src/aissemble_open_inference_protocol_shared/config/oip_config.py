###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
import os
from krausening.properties import PropertyManager


class OIPConfig:
    """
    Configurations for OIP
    """

    DEFAULT_ALGORITHM = "HS256"
    DEFAULT_PDP_URL = "http://localhost:8080/pdp"

    DEFAULT_GRPC_HOST = "0.0.0.0"
    DEFAULT_GRPC_PORT = "8081"
    DEFAULT_GRPC_WORKERS = "3"
    DEFAULT_AUTH_ENABLED = "true"

    DEFAULT_FASTAPI_HOST = "127.0.0.1"
    DEFAULT_FASTAPI_PORT = "8082"
    DEFAULT_FASTAPI_RELOAD = "True"

    def __init__(self):
        self.properties = PropertyManager.get_instance().get_properties(
            "oip.properties"
        )

    #########################
    # Authorization
    #########################

    @property
    def auth_enabled(self) -> bool:
        """
        Whether authorization is enabled for the server.
        If auth_enabled is set to true with no protected endpoints specified then all endpoints are protected.
        """
        value = self.properties.getProperty("auth_enabled", self.DEFAULT_AUTH_ENABLED)
        environ_override = os.getenv("AUTH_ENABLED")
        enabled = environ_override if environ_override else value
        return str(enabled).lower() == "true"

    def auth_secret(self):
        """
        Returns the auth secret key
        """
        value = self.properties.getProperty("auth_secret", "")
        environ_override = os.getenv("AUTH_SECRET")
        return environ_override if environ_override else value

    def auth_algorithm(self):
        """
        Returns the auth algorithm
        """
        value = self.properties.getProperty("auth_algorithm", self.DEFAULT_ALGORITHM)
        environ_override = os.getenv("AUTH_ALGORITHM")
        return environ_override if environ_override else value

    def pdp_url(self):
        """
        Returns the PDP url
        """
        value = self.properties.getProperty("pdp_url", self.DEFAULT_PDP_URL)
        environ_override = os.getenv("OIP_PDP_URL")
        return environ_override if environ_override else value

    #########################
    # gRPC
    #########################
    @property
    def grpc_host(self) -> str:
        value = self.properties.getProperty("grpc_host", self.DEFAULT_GRPC_HOST)
        environ_override = os.getenv("GRPC_HOST")
        return environ_override if environ_override else value

    @property
    def grpc_port(self) -> str:
        value = self.properties.getProperty("grpc_port", self.DEFAULT_GRPC_PORT)
        environ_override = os.getenv("GRPC_PORT")
        return environ_override if environ_override else value

    @property
    def grpc_workers(self) -> int:
        value = self.properties.getProperty("grpc_workers", self.DEFAULT_GRPC_WORKERS)
        environ_override = os.getenv("GRPC_WORKERS")
        worker_count = environ_override if environ_override else value
        return int(worker_count)

    @property
    def grpc_protected_endpoints(self) -> set[str]:
        """
        Returns a set of protected endpoint strings.
        """
        environ_override = os.getenv("GRPC_PROTECTED_ENDPOINTS")
        if environ_override:
            endpoints = [ep.strip() for ep in environ_override.split(",") if ep.strip()]
        else:
            value = self.properties.getProperty("grpc_protected_endpoints", "")
            endpoints = [ep.strip() for ep in value.split(",") if ep.strip()]
        return set(endpoints)

    #########################
    # FastAPI
    #########################
    # , reload=reload, host=host, port=port
    @property
    def fastapi_host(self) -> str:
        value = self.properties.getProperty("fastapi_host", self.DEFAULT_FASTAPI_HOST)
        environ_override = os.getenv("FASTAPI_HOST")
        return environ_override if environ_override else value

    @property
    def fastapi_port(self) -> int:
        value = self.properties.getProperty("fastapi_port", self.DEFAULT_FASTAPI_PORT)
        environ_override = os.getenv("FASTAPI_PORT")
        return int(environ_override if environ_override else value)

    @property
    def fastapi_reload(self) -> bool:
        value = self.properties.getProperty(
            "fastapi_reload", self.DEFAULT_FASTAPI_RELOAD
        )
        environ_override = os.getenv("FASTAPI_RELOAD")
        return bool(environ_override if environ_override else value)
