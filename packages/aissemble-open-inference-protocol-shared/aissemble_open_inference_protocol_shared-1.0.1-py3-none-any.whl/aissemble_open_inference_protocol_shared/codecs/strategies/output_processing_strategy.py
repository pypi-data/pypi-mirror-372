###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

from typing import List, Optional
from aissemble_open_inference_protocol_shared.types.dataplane import (
    Parameters,
    RequestOutput,
    ResponseOutput,
    InferenceRequest,
    InferenceResponse,
)
from aissemble_open_inference_protocol_shared.codecs.utils import (
    get_content_type,
    encode_response_output,
)


def _get_payload(res_output: ResponseOutput) -> object:
    """Extracts payload from a ResponseOutput."""
    return res_output.data.root if hasattr(res_output.data, "root") else res_output.data


def _determine_content_type(
    handler_params: Parameters,
    request_output: RequestOutput,
    request_content_type: str,
) -> Optional[str]:
    """Determines the content type based on a priority order."""
    handler_content_type = get_content_type(handler_params)
    if handler_content_type:
        return handler_content_type

    request_output_content_type = get_content_type(request_output)
    if request_output_content_type:
        return request_output_content_type

    if request_content_type:
        return request_content_type

    return None


class OutputProcessingStrategy:
    """Base class for output processing strategies."""

    def __init__(self, request: InferenceRequest, result: InferenceResponse):
        self.request = request
        self.result = result
        self.request_content_type = get_content_type(request)

    def process_outputs(self) -> List[ResponseOutput]:
        raise NotImplementedError


class ProcessAllOutputsStrategy(OutputProcessingStrategy):
    """Strategy to process all outputs when none are specified in the request."""

    def process_outputs(self) -> List[ResponseOutput]:
        outputs = []
        for handler_output in self.result.outputs:
            request_output = RequestOutput(name=handler_output.name)
            handler_params = getattr(handler_output, "parameters", None)
            content_type = _determine_content_type(
                handler_params, request_output, self.request_content_type
            )
            if content_type:
                if not getattr(request_output, "parameters", None):
                    request_output.parameters = Parameters()
                request_output.parameters.content_type = content_type

            payload = _get_payload(handler_output)
            encoded = encode_response_output(payload, request_output)
            if encoded:
                outputs.append(encoded)
            else:
                outputs.append(handler_output)
        return outputs


class ProcessRequestedOutputsStrategy(OutputProcessingStrategy):
    """Strategy to process only the outputs specified in the request."""

    def process_outputs(self) -> List[ResponseOutput]:
        outputs = []
        result_outputs_map = {
            res_output.name: res_output for res_output in self.result.outputs
        }
        request_outputs = getattr(self.request, "outputs", [])

        for request_output in request_outputs:
            handler_output = result_outputs_map.get(request_output.name)
            handler_params = (
                getattr(handler_output, "parameters", None) if handler_output else None
            )
            content_type = _determine_content_type(
                handler_params, request_output, self.request_content_type
            )
            payload = _get_payload(handler_output) if handler_output else None

            if content_type and payload is not None:
                encoded = encode_response_output(payload, request_output)
                if encoded:
                    if not getattr(encoded.parameters, "content_type", None):
                        encoded.parameters.content_type = content_type
                    outputs.append(encoded)
                    continue

            if handler_output:
                outputs.append(handler_output)
            elif isinstance(request_output, ResponseOutput):
                outputs.append(request_output)
        return outputs
