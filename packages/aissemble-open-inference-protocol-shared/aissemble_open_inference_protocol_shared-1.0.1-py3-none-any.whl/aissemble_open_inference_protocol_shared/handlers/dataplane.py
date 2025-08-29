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
from typing import Optional

from fastapi import status, HTTPException

from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceRequest,
    InferenceResponse,
    ModelMetadataResponse,
    ModelReadyResponse,
    ServerReadyResponse,
    ServerLiveResponse,
    ServerMetadataResponse,
)


class DataplaneHandler(ABC):
    @abstractmethod
    def infer(
        self,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        pass

    @abstractmethod
    def model_metadata(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        pass

    @abstractmethod
    def model_ready(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelReadyResponse:
        pass

    def server_ready(self) -> ServerReadyResponse:
        return ServerReadyResponse(live=True)

    def server_live(self) -> ServerLiveResponse:
        return ServerLiveResponse(live=True)

    def server_metadata(self) -> ServerMetadataResponse:
        return ServerMetadataResponse(
            name="Inference Server", version="1.0", extensions=[]
        )


class DefaultHandler(DataplaneHandler):
    def infer(
        self,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def model_metadata(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelMetadataResponse:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def model_ready(
        self,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> ModelReadyResponse:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
