###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

###
# Acknowledgment:
# This implementation is inspired by the MLServer project.
# It follows similar design principles to integrate with the aissemble-open-inference-protocol.
# See MLServer’s license for details:
# Apache License Version 2.0 (https://github.com/SeldonIO/MLServer/blob/master/LICENSE)
###

from typing import Any, ClassVar, Type, Union, Optional

from aissemble_open_inference_protocol_shared.types.dataplane import (
    RequestInput,
    ResponseOutput,
    InferenceRequest,
    InferenceResponse,
)
from krausening.logging import LogManager

logger = LogManager.get_instance().get_logger("Codec")

InputCodecType = Union[Type["InputCodec"], "InputCodec"]
RequestCodecType = Union[Type["RequestCodec"], "RequestCodec"]


class InputCodec:
    ContentType: ClassVar[str] = ""

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """Return True if this codec can encode/decode the given payload."""
        return False

    @classmethod
    def encode_input(cls, name: str, payload: Any, **kwargs) -> RequestInput:
        """Encode Python payload into a RequestInput."""
        raise NotImplementedError()

    @classmethod
    def decode_input(cls, request_input: RequestInput) -> Any:
        """Decode RequestInput into Python payload."""
        raise NotImplementedError()

    @classmethod
    def encode_output(cls, name: str, payload: Any, **kwargs) -> ResponseOutput:
        """Encode Python payload into a ResponseOutput."""
        raise NotImplementedError()

    @classmethod
    def decode_output(cls, response_output: ResponseOutput) -> Any:
        """Decode ResponseOutput into Python payload."""
        raise NotImplementedError()


class RequestCodec:
    ContentType: ClassVar[str] = ""

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """Return True if this codec can encode/decode the given payload."""
        return False

    @classmethod
    def encode_request(cls, payload: Any, **kwargs) -> InferenceRequest:
        """Encode Python payload into an InferenceRequest."""
        raise NotImplementedError()

    @classmethod
    def decode_request(cls, request: InferenceRequest) -> Any:
        """Decode InferenceRequest into Python payload."""
        raise NotImplementedError()

    @classmethod
    def encode_response(
        cls,
        model_name: str,
        payload: Any,
        model_version: Optional[str] = None,
        **kwargs,
    ) -> InferenceResponse:
        """Encode Python payload into an InferenceResponse."""
        raise NotImplementedError()

    @classmethod
    def decode_response(cls, response: InferenceResponse) -> Any:
        """Decode InferenceResponse into Python payload."""
        raise NotImplementedError()
