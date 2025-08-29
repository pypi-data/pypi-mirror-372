# aiSSEMBLE Open Inference Protocol&trade; Shared Utils
Contains common functionality shared across multiple interfaces

## Content Type Precedence

When constructing an `InferenceResponse`, the `build_inference_response` utility determines the `content_type` for each output using the following precedence chain:

1. **Handler Output Content Type**: If the handler's output specifies a `content_type`, it takes highest precedence and is used directly.
2. **Per-Output Content Type**: If `request.outputs` is set, the `content_type` specified for each output is used.
3. **Request-Level Content Type**: If no per-output type is set, falls back to the request-level `content_type` (from `request.parameters.content_type`).
4. **Default Fallback**: If none of the above are set, defaults to `None` as the content type.

This ensures that the most specific content type is always used, with clear and predictable fallback behavior.

## Examples
For working examples and more details on shared features, configuration options, and usage, refer to the [Examples](https://github.com/boozallen/aissemble-open-inference-protocol/blob/dev/aissemble-open-inference-protocol-examples/README.md#shared) documentation.