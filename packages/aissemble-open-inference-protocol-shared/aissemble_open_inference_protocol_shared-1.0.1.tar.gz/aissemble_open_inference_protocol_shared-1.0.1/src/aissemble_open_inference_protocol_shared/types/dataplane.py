###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel
from pydantic import Field, RootModel, ConfigDict
import numpy as np
from krausening.logging import LogManager

logger = LogManager.get_instance().get_logger("Dataplane")

DYNAMIC_SHAPE_SPECIFIER = -1


class Parameters(BaseModel):
    content_type: Optional[str] = None
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class Datatype(str, Enum):
    BOOL = "BOOL"
    UINT8 = "UINT8"
    UINT16 = "UINT16"
    UINT32 = "UINT32"
    UINT64 = "UINT64"
    INT8 = "INT8"
    INT16 = "INT16"
    INT32 = "INT32"
    INT64 = "INT64"
    FP16 = "FP16"
    FP32 = "FP32"
    FP64 = "FP64"
    BYTES = "BYTES"


class TensorData(RootModel[Union[List, Any]]):
    root: Union[List, Any] = Field(..., title="TensorData")

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, idx):
        return self.root[idx]

    def __len__(self):
        return len(self.root)

    def validate_oip(self, shape: List[int], datatype: Datatype) -> None:
        validate_shape(shape, self.root)
        validate_datatype(datatype, flatten(self.root))


class RequestOutput(BaseModel):
    name: str
    parameters: Optional[Parameters] = None


class RequestInput(BaseModel):
    name: str
    shape: List[int]
    datatype: Datatype
    parameters: Optional[Parameters] = None
    data: TensorData

    def validate_oip(self) -> None:
        self.data.validate_oip(self.shape, self.datatype)


class ResponseOutput(BaseModel):
    name: str
    shape: List[int]
    datatype: Datatype
    parameters: Optional[Parameters] = None
    data: TensorData

    def validate_oip(self) -> None:
        self.data.validate_oip(self.shape, self.datatype)


class InferenceResponse(BaseModel):
    model_name: str
    model_version: Optional[str] = None
    id: Optional[str] = None
    parameters: Optional[Parameters] = None
    outputs: List[ResponseOutput]

    def validate_oip(self) -> None:
        if self.outputs:
            for output_value in self.outputs:
                try:
                    output_value.validate_oip()
                except Exception as e:
                    raise type(e)(f"output ('{output_value.name}'): {e}") from e
        else:
            logger.info(
                f"InferenceResponse for model '{self.model_name}' contained no outputs."
            )


class InferenceRequest(BaseModel):
    id: Optional[str] = None
    parameters: Optional[Parameters] = None
    inputs: List[RequestInput]
    outputs: Optional[List[RequestOutput]] = None

    def validate_oip(self) -> None:
        if not self.inputs:
            raise ValueError("InferenceRequest does not contain any inputs")
        for input_value in self.inputs:
            try:
                input_value.validate_oip()
            except Exception as e:
                raise type(e)(f"input ('{input_value.name}'): {e}") from e


class MetadataTensor(BaseModel):
    name: str
    datatype: Datatype
    shape: List[int]


class ModelMetadataResponse(BaseModel):
    name: str
    versions: Optional[List[str]] = None
    platform: str
    inputs: List[MetadataTensor]
    outputs: List[MetadataTensor]


class ModelMetadataErrorResponse(BaseModel):
    error: str


class ModelReadyResponse(BaseModel):
    name: str
    ready: bool


class ServerReadyResponse(BaseModel):
    live: bool


class ServerLiveResponse(BaseModel):
    live: bool


class ServerMetadataResponse(BaseModel):
    name: str
    version: str
    extensions: List[str]


class ServerMetadataErrorResponse(BaseModel):
    error: str


def flatten(data: Union[List[Any], Any]) -> List[Any]:
    """
    Recursively flatten nested lists into a single flat list of scalars
    """
    # if data is scalar, wrap it in a list and return
    if not isinstance(data, list):
        return [data]

    flat_data = []
    for item in data:
        # extend flat_data list by appending elements from the iterable
        flat_data.extend(flatten(item))

    return flat_data


def get_actual_shape(data):
    """
    Returns a list of lengths at each nesting level. Assumes shape is rectangular.
    """
    shape = []
    while isinstance(data, list):
        shape.append(len(data))
        data = data[0]

    return shape


def validate_datatype(expected_datatype: Datatype, flat_data: List[Any]) -> None:
    """
    Validates that all elements in flat_data match the expected Datatype.
    Raises TypeError for mismatches and ValueError for unsupported types.
    """
    type_checks = {
        Datatype.BOOL: lambda x: isinstance(x, bool),
        Datatype.UINT8: lambda x: isinstance(x, int),
        Datatype.UINT16: lambda x: isinstance(x, int),
        Datatype.UINT32: lambda x: isinstance(x, int),
        Datatype.UINT64: lambda x: isinstance(x, int),
        Datatype.INT8: lambda x: isinstance(x, int),
        Datatype.INT16: lambda x: isinstance(x, int),
        Datatype.INT32: lambda x: isinstance(x, int),
        Datatype.INT64: lambda x: isinstance(x, int),
        Datatype.FP16: lambda x: isinstance(x, float),
        Datatype.FP32: lambda x: isinstance(x, float),
        Datatype.FP64: lambda x: isinstance(x, float),
        Datatype.BYTES: lambda x: isinstance(x, (bytes, str)),
    }

    # look up and return the validation function for the expected_datatype if found, otherwise return None
    is_datatype = type_checks.get(expected_datatype)

    if not is_datatype:
        raise ValueError(f"Unsupported datatype - {expected_datatype}")

    # validate datatype of each element in flat_data
    for i, value in enumerate(flat_data):
        if not is_datatype(value):
            raise TypeError(
                f"Datatype mismatch - element at index {i} is of type {type(value).__name__}, "
                f"but expected type compatible with {expected_datatype}"
            )


def validate_shape(expected_shape: List[int], data: Union[List[Any], Any]) -> None:
    """
    Validates that the data (flat or nested) contains the correct number of elements based on the expected shape.
    If nested, also ensures the structure is rectangular (no ragged lists) and matches the nested pattern.
    """
    # check that flattened data has the correct number of elements
    if not shape_is_valid(expected_shape, data):
        raise ValueError(
            f"Shape mismatch - declared {expected_shape} "
            f", but got {get_actual_shape(data)}"
        )

    # if data is nested and multidimensional, then check for rectangular structure & nested pattern
    if (
        expected_shape
        and isinstance(data, list)
        and len(expected_shape) > 1
        and any(isinstance(elt, list) for elt in data)
        and DYNAMIC_SHAPE_SPECIFIER not in expected_shape
    ):
        # np.array creates a true N-dimensional object array only if the data is fully rectangular
        # otherwise, it returns an array of separate list objects.
        data_array = np.array(data, dtype=object)

        # check for ragged lists (differing lengths)
        ragged = [elt for elt in data_array.flat if isinstance(elt, list)]
        if ragged:
            raise ValueError("Malformed tensor - nested lists are not rectangular")

        # check nested pattern
        actual_shape = get_actual_shape(data)
        if expected_shape != actual_shape:
            raise ValueError(
                f"Shape mismatch in nested representation - expected {expected_shape}, but got {actual_shape}"
            )


def shape_is_valid(expected_shape, tensor_data):
    shape_is_valid = False
    actual_shape = get_actual_shape(tensor_data)
    if DYNAMIC_SHAPE_SPECIFIER in expected_shape:
        logger.info(f"Inference request with dynamic input shape '{expected_shape}'.")
        shape_is_valid = _expected_equals_actual_with_wildcard(
            expected_shape, actual_shape
        )
    else:
        shape_is_valid = _shape_is_smooth_and_expected(expected_shape, tensor_data)

    return shape_is_valid


def _shape_is_smooth_and_expected(expected_shape, tensor_data):
    shape_is_smooth = False
    flat = flatten(tensor_data)
    expected_count = int(np.prod(expected_shape)) if expected_shape else 1
    if len(flat) == expected_count:
        # if the flattened data length equals the expected matrix product
        # then the data is considered smooth (not ragged)
        shape_is_smooth = True

    return shape_is_smooth


def _expected_equals_actual_with_wildcard(
    expected, actual, wildcard=DYNAMIC_SHAPE_SPECIFIER
):
    if len(expected) != len(actual):
        return False

    return all(a == b or a == wildcard for a, b in zip(expected, actual))
