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
# Apache License, Version 2.0 (https://github.com/SeldonIO/MLServer/blob/master/LICENSE)
###

from typing import Dict, Any, Optional, Iterable, Union
from aissemble_open_inference_protocol_shared.codecs.codec import (
    InputCodec,
    RequestCodec,
    InputCodecType,
    RequestCodecType,
)
from krausening.logging import LogManager


class CodecRegistry:
    """
    Central registry for mapping content_type strings to codec classes.
    Maintains separate registries for InputCodecs (per-tensor)
    and RequestCodecs (whole-request).
    """

    logger = LogManager.get_instance().get_logger("CodecRegistry")

    def __init__(
        self,
        input_codecs: Dict[str, InputCodecType] = None,
        request_codecs: Dict[str, RequestCodecType] = None,
    ):
        self.input_codecs = input_codecs or {}
        self.request_codecs = request_codecs or {}

    def find_codec_by_payload(
        self, payload: Any, codecs: Iterable[Union[RequestCodec, InputCodec]]
    ) -> Optional[Union[RequestCodec, InputCodec]]:
        """
        Return the first codec whose can_encode(payload) is True, or log a warning if none or multiple matching codecs are found.
        """
        matching_codecs = []
        for codec in codecs:
            if codec.can_encode(payload):
                matching_codecs.append(codec)

        if len(matching_codecs) == 0:
            self.logger.warning(
                "No matching codec found for payload of type %s", type(payload)
            )
            return None

        matching_codec = matching_codecs[0]
        if len(matching_codecs) > 1:
            self.logger.warning(
                "%d matching codecs found for payload of type %s... Using first matching codec: %s",
                len(matching_codecs),
                type(payload),
                matching_codec.ContentType,
            )

        return matching_codec

    def register_input_codec(self, content_type: str, codec: InputCodecType):
        """
        Register an InputCodec class under the given content_type string.
        """
        self.input_codecs[content_type] = codec

    def find_input_codec(
        self, content_type: Optional[str] = None, payload: Optional[Any] = None
    ) -> Optional[InputCodecType]:
        """
        Look up an InputCodec by content_type, or fallback to matching by payload if none provided.
        """
        if content_type:
            return self.input_codecs.get(content_type)
        elif payload:
            return self.find_input_codec_by_payload(payload)
        return None

    def find_input_codec_by_payload(self, payload: Any) -> Optional[InputCodecType]:
        """
        Find an InputCodec by scanning all registered codecs and checking can_encode(payload).
        """
        return self.find_codec_by_payload(payload, self.input_codecs.values())

    def register_request_codec(self, content_type: str, codec: RequestCodecType):
        """
        Register a RequestCodec class under the given content_type string.
        """
        self.request_codecs[content_type] = codec

    def find_request_codec(
        self, content_type: Optional[str] = None, payload: Optional[Any] = None
    ) -> Optional[RequestCodecType]:
        """
        Look up an RequestCodec by content_type, or fallback to matching by payload if none provided.
        """
        if content_type:
            return self.request_codecs.get(content_type)
        elif payload:
            return self.find_request_codec_by_payload(payload)
        return None

    def find_request_codec_by_payload(self, payload: Any) -> Optional[RequestCodecType]:
        """
        Find a RequestCodec by scanning all registered codecs and checking can_encode(payload).
        """
        return self.find_codec_by_payload(payload, self.request_codecs.values())


# Singleton registry for app
codec_registry = CodecRegistry()

# Module-level aliases
find_input_codec = codec_registry.find_input_codec
find_input_codec_by_payload = codec_registry.find_input_codec_by_payload
find_request_codec = codec_registry.find_request_codec
find_request_codec_by_payload = codec_registry.find_request_codec_by_payload


# Decorator factories
def register_input_codec(CodecClass: InputCodecType):
    """
    Class decorator to register an InputCodec under its ContentType.
    """
    if CodecClass.ContentType:
        codec_registry.register_input_codec(CodecClass.ContentType, CodecClass)
    return CodecClass


def register_request_codec(CodecClass: RequestCodecType):
    """
    Class decorator to register a RequestCodec under its ContentType.
    """
    if CodecClass.ContentType:
        codec_registry.register_request_codec(CodecClass.ContentType, CodecClass)
    return CodecClass
