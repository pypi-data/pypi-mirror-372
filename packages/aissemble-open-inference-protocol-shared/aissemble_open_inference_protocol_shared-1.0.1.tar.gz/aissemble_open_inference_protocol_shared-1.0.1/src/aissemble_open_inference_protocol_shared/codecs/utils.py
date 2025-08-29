###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

from typing import Any, Optional, Union, List, Dict
from aissemble_open_inference_protocol_shared.codecs.registry import (
    find_input_codec,
    find_input_codec_by_payload,
    find_request_codec,
    find_request_codec_by_payload,
)
from aissemble_open_inference_protocol_shared.codecs.codec import (
    InputCodecType,
    RequestCodecType,
    RequestCodec,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    Parameters,
    RequestInput,
    RequestOutput,
    ResponseOutput,
    InferenceRequest,
    InferenceResponse,
    MetadataTensor,
)
from krausening.logging import LogManager

INPUT = "input"
OUTPUT = "output"
DECODED_ATTR = "decoded_payload"
PARAMETERS = "parameters"
CONTENT_TYPE = "content_type"

InputOrOutput = Union[RequestInput, ResponseOutput]
Codec = Union[InputCodecType, RequestCodecType]
ParameterizedObject = Union[
    RequestInput, ResponseOutput, RequestOutput, InferenceRequest, InferenceResponse
]


def inject_batch_dimension(shape: List[int]) -> List[int]:
    """
    Ensure that 1-dimensional shapes assume `[N] == [N, 1]`, where N=len(data)
    """
    return shape if len(shape) > 1 else shape + [1]


def get_content_type(
    obj: ParameterizedObject, metadata: Optional[MetadataTensor] = None
) -> Optional[str]:
    """
    Read the `content_type` tag from a ParameterizedObject or its metadata.
    """
    content_type = getattr(getattr(obj, PARAMETERS, None), CONTENT_TYPE, None)
    if content_type:
        return content_type
    if metadata:
        return getattr(getattr(metadata, PARAMETERS, None), CONTENT_TYPE, None)
    return None


def save_decoded(obj: ParameterizedObject, decoded_payload: Any):
    """
    Store a decoded Python payload on the object’s parameters.decoded_payload.
    """
    if not getattr(obj, PARAMETERS, None):
        obj.parameters = Parameters()
    setattr(obj.parameters, DECODED_ATTR, decoded_payload)


def has_decoded(obj: ParameterizedObject) -> bool:
    """
    Return True if `obj.parameters.decoded_payload` exists.
    """
    return getattr(obj, PARAMETERS, None) is not None and hasattr(
        obj.parameters, DECODED_ATTR
    )


def get_decoded(obj: ParameterizedObject) -> Any:
    """
    Retrieve the saved `decoded_payload` from `obj.parameters`.
    """
    return getattr(obj.parameters, DECODED_ATTR, None)


def get_decoded_or_raw(obj: ParameterizedObject) -> Any:
    """
    Returns saved decoded payload if it exists. Otherwise, returns the raw data.
    """
    if has_decoded(obj):
        return get_decoded(obj)
    if isinstance(obj, (RequestInput, ResponseOutput)):
        return obj.data
    return obj


def decode_request_input(request_input: RequestInput) -> Optional[Any]:
    """
    Decode a single RequestInput using its content_type tag.
    """
    content_type = get_content_type(request_input)

    if content_type is None:
        return None

    codec = find_input_codec(content_type)
    if codec is None:
        return None

    decoded_payload = codec.decode_input(request_input)

    save_decoded(request_input, decoded_payload)
    return decoded_payload


def decode_inference_request(inference_request: InferenceRequest) -> Optional[Any]:
    """
    Decode all inputs, then optionally decode the entire request (if request-level content_type was set).
    """
    for request in inference_request.inputs:
        decode_request_input(request)

    content_type = get_content_type(inference_request)

    if content_type:
        codec = find_request_codec(content_type)
        if codec is not None:
            decoded_payload = codec.decode_request(inference_request)
            save_decoded(inference_request, decoded_payload)
            return decoded_payload

    return inference_request


def encode_response_output(
    payload: Any,
    request_output: RequestOutput,
    metadata_outputs: Optional[Dict[str, MetadataTensor]] = None,
) -> Optional[ResponseOutput]:
    """
    Encode a single Python result into a ResponseOutput.
    """
    if metadata_outputs is None:
        metadata_outputs = {}

    output_metadata = metadata_outputs.get(request_output.name)
    content_type = get_content_type(request_output, output_metadata)

    if content_type:
        codec = find_input_codec(content_type)
    else:
        codec = find_input_codec_by_payload(payload)

    if not codec:
        return None
    return codec.encode_output(name=request_output.name, payload=payload)


def encode_inference_response(
    model_name: str, payload: Any, model_version: Optional[str] = None
) -> Optional[InferenceResponse]:
    """
    Encode a Python object into a full InferenceResponse via a RequestCodec.
    """
    codec = find_request_codec_by_payload(payload)

    if not codec:
        return None

    return codec.encode_response(
        model_name=model_name, payload=payload, model_version=model_version
    )


def build_inference_response(
    model_name: str,
    request: InferenceRequest,
    result: InferenceResponse,
    model_version: Optional[str] = None,
) -> InferenceResponse:
    """
    Construct an InferenceResponse by encoding a handler's raw Python result according to content_type
    1. Handler output content_type takes precedence.
    2. Try per-output content_type (if request.outputs is set).
    3. Fallback to a request-level content_type (if request.parameters.content_type is set).
    4. Otherwise, fallback to None content_type.
    """
    # Import here to avoid circular import
    from aissemble_open_inference_protocol_shared.codecs.strategies.output_processing_strategy import (
        ProcessAllOutputsStrategy,
        ProcessRequestedOutputsStrategy,
    )

    request_outputs = getattr(request, "outputs", None) or []
    if not request_outputs:
        strategy = ProcessAllOutputsStrategy(request, result)
    else:
        strategy = ProcessRequestedOutputsStrategy(request, result)

    outputs = strategy.process_outputs()

    return InferenceResponse(
        model_name=model_name,
        model_version=model_version,
        parameters=getattr(result, "parameters", None),
        outputs=outputs,
    )


class SingleTensorRequestCodec(RequestCodec):
    """
    Base class for request-level codecs that wrap a single tensor.
    """

    logger = LogManager.get_instance().get_logger("SingleTensorRequestCodec")
    InputCodec: Optional[InputCodecType] = None

    @classmethod
    def can_encode(cls, payload: Any) -> bool:
        return cls.InputCodec is not None and cls.InputCodec.can_encode(payload)

    @classmethod
    def encode_request(cls, payload: Any, **kwargs) -> InferenceRequest:
        if cls.InputCodec is None:
            cls.logger.error("No InputCodec set for %s", cls)
        input = cls.InputCodec.encode_input(
            name=f"{INPUT}-0", payload=payload, **kwargs
        )
        return InferenceRequest(
            inputs=[input], parameters=Parameters(content_type=cls.ContentType)
        )

    @classmethod
    def decode_request(cls, request: InferenceRequest) -> Any:
        if len(request.inputs) != 1:
            cls.logger.error("'%s' only supports single input", cls.ContentType)
        first_input = request.inputs[0]
        if not has_decoded(first_input) and cls.InputCodec:
            decoded_payload = cls.InputCodec.decode_input(first_input)
            save_decoded(first_input, decoded_payload)
        return get_decoded_or_raw(first_input)

    @classmethod
    def encode_response(
        cls,
        model_name: str,
        payload: Any,
        model_version: Optional[str] = None,
        **kwargs,
    ) -> InferenceResponse:
        if cls.InputCodec is None:
            cls.logger.error("No InputCodec set for %s", cls)
        output = cls.InputCodec.encode_output(
            name=f"{OUTPUT}-0", payload=payload, **kwargs
        )
        return InferenceResponse(
            model_name=model_name,
            model_version=model_version,
            parameters=Parameters(content_type=cls.ContentType),
            outputs=[output],
        )

    @classmethod
    def decode_response(cls, response: InferenceResponse) -> Any:
        if len(response.outputs) != 1:
            cls.logger.error("'%s' only supports single output", cls.ContentType)
        first_output = response.outputs[0]
        if not has_decoded(first_output) and cls.InputCodec:
            decoded_payload = cls.InputCodec.decode_output(first_output)
            save_decoded(first_output, decoded_payload)
        return get_decoded_or_raw(first_output)
