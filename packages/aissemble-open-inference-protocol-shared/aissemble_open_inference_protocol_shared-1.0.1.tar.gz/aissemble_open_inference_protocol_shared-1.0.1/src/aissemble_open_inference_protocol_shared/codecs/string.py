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

from typing import List, Any, Union
from aissemble_open_inference_protocol_shared.codecs.codec import InputCodec
from aissemble_open_inference_protocol_shared.codecs.registry import (
    register_input_codec,
    register_request_codec,
)
from aissemble_open_inference_protocol_shared.codecs.utils import (
    InputOrOutput,
    SingleTensorRequestCodec,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    Parameters,
    RequestInput,
    ResponseOutput,
)
from krausening.logging import LogManager

logger = LogManager.get_instance().get_logger("StringCodec")

DEFAULT_STR_CODEC = "utf-8"
BytesStringList = Union[bytes, str]
PayloadList = Union[BytesStringList, List[BytesStringList]]


def encode_str(s: str) -> bytes:
    try:
        return s.encode(DEFAULT_STR_CODEC)
    except UnicodeEncodeError as e:
        raise ValueError(
            f"String could not be encoded using '{DEFAULT_STR_CODEC}': {e}"
        ) from e


def decode_str(b: Any) -> str:
    if b is None:
        return None
    if isinstance(b, bytes):
        return b.decode(DEFAULT_STR_CODEC)
    if isinstance(b, str):
        return b
    return ""


def decode_input_or_output(input_or_output: InputOrOutput) -> List[str]:
    raw_data = input_or_output.data.root
    items = raw_data if isinstance(raw_data, list) else [raw_data]
    return [decode_str(x) for x in items]


# Decorator adds StringCodec to the global input-codec registry under "str"
@register_input_codec
class StringCodec(InputCodec):
    ContentType = "str"

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        """
        Return True if given codec can handle the given payload.
        """
        return isinstance(payload, list) and all(isinstance(x, str) for x in payload)

    @classmethod
    def encode_input(
        cls, name: str, payload: List[str], use_bytes: bool = True, **kwargs
    ) -> RequestInput:
        """
        Encode a Python list of strings into a RequestInput.
        """
        output = cls.encode_output(name=name, payload=payload, use_bytes=use_bytes)
        return RequestInput(
            name=output.name,
            datatype=output.datatype,
            shape=output.shape,
            data=output.data,
            parameters=output.parameters,
        )

    @classmethod
    def encode_output(
        cls, name: str, payload: List[str], use_bytes: bool = True, **kwargs
    ) -> ResponseOutput:
        """
        Encode a Python list of strings into a ResponseOutput.
        """
        if use_bytes:
            data = [encode_str(x) for x in payload]
        else:
            data = payload

        shape = [len(payload), 1]
        return ResponseOutput(
            name=name,
            datatype="BYTES",
            shape=shape,
            data=list(data),
            parameters=Parameters(content_type=cls.ContentType),
        )

    @classmethod
    def decode_input(cls, request_input: RequestInput) -> List[str]:
        """
        Decode a RequestInput (BYTES tensor) back into a list of Python strings.
        """
        return decode_input_or_output(request_input)

    @classmethod
    def decode_output(cls, response_output: ResponseOutput) -> List[str]:
        """
        Decode a ResponseOutput (BYTES tensor) back into a list of Python strings.
        """
        return decode_input_or_output(response_output)


@register_request_codec
class StringRequestCodec(SingleTensorRequestCodec):
    """
    Wraps StringCodec into a full InferenceRequest/Response by decoding
    the first input/output tensor as a Python list of strings and
    re-encoding it on output.
    """

    InputCodec = StringCodec
    ContentType = StringCodec.ContentType
