###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from typing import Mapping
from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2 import (
    ModelInferResponse,
    InferParameter,
    InferTensorContents,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceResponse,
    ResponseOutput,
    InferenceRequest,
    RequestInput,
    RequestOutput,
    Parameters,
    TensorData,
    Datatype,
)
import aissemble_open_inference_protocol_grpc.mappers.utils as mapper_utils
from krausening.logging import LogManager

_FIELDS = {
    Datatype.BOOL: "bool_contents",
    Datatype.UINT8: "uint_contents",
    Datatype.UINT16: "uint_contents",
    Datatype.UINT32: "uint_contents",
    Datatype.UINT64: "uint64_contents",
    Datatype.INT8: "int_contents",
    Datatype.INT16: "int_contents",
    Datatype.INT32: "int_contents",
    Datatype.INT64: "int64_contents",
    Datatype.FP16: "bytes_contents",
    Datatype.FP32: "fp32_contents",
    Datatype.FP64: "fp64_contents",
    Datatype.BYTES: "bytes_contents",
}


class ModelInferenceResponseMapper:
    logger = LogManager.get_instance().get_logger("ModelInferenceResponseMapper")

    def to_model_inference_response(
        self, inference_response: InferenceResponse
    ) -> ModelInferResponse:
        """
        Maps Inference Response object to gRPC Model Inference Response
        :param inference_response: the Inference Response
        :return: the equivalent Model Inference Response object
        """
        model_inference_response = ModelInferResponse(
            model_name=inference_response.model_name,
            outputs=[
                self._output_to_inference_tensor(output)
                for output in inference_response.outputs
            ],
        )
        if inference_response.id is not None:
            model_inference_response.id = inference_response.id

        if inference_response.model_version is not None:
            model_inference_response.model_version = inference_response.model_version

        if inference_response.parameters:
            mapper_utils.merge_infer_parameters(
                model_inference_response.parameters,
                self._inference_response_to_params(inference_response.parameters),
            )
        return model_inference_response

    def _output_to_inference_tensor(
        self, response_output: ResponseOutput
    ) -> ModelInferResponse.InferOutputTensor:
        """
        Maps Inference Response ResponseOutput object to a Model Inference Response output
        :param response_output: the response output to convert
        :return: A mapped Model Inference Response's output tensor
        """
        infer_output_tensor = ModelInferResponse.InferOutputTensor(
            name=response_output.name,
            shape=response_output.shape,
            datatype=str(response_output.datatype),
            contents=self._converter_from_types(
                response_output.data, datatype=Datatype(response_output.datatype)
            ),
        )

        if response_output.parameters:
            mapper_utils.merge_infer_parameters(
                infer_output_tensor.parameters,
                self._inference_response_to_params(response_output.parameters),
            )

        return infer_output_tensor

    def _converter_from_types(
        self, tensor_contents: TensorData, datatype: Datatype
    ) -> InferTensorContents:
        contents = self._create_field_mapping(tensor_contents, datatype)
        return InferTensorContents(**contents)

    def _inference_response_to_params(
        self, inference_response_parameters: Parameters
    ) -> Mapping[str, InferParameter]:
        """
        Convert an InferenceResponse parameters object into a dictionary of gRPC model parameters
        :param inference_response_parameters: an InferenceResponse parameters object containing key-value pairs from the response
        :return: a dictionary where each key maps to a gRPC InferParameter with the appropriate type field set
        """
        raw_param_dict = inference_response_parameters.model_dump(by_alias=True)
        converted_model_params = {}
        for model_param_name, model_param_value in raw_param_dict.items():
            if isinstance(model_param_value, bool):
                grpc_type_key = "bool_param"
            elif isinstance(model_param_value, int):
                grpc_type_key = "int64_param"
            elif isinstance(model_param_value, str):
                grpc_type_key = "string_param"
            elif isinstance(model_param_value, float):
                grpc_type_key = "double_param"
            else:
                self.logger.info(
                    f"Skipping conversion for the following parameters due to unsupported types: {model_param_name}={model_param_value} ({type(model_param_value)})"
                )
                continue

            converted_model_params[model_param_name] = InferParameter(
                **{grpc_type_key: model_param_value}
            )
        return converted_model_params

    def _create_field_mapping(
        self, type_object: TensorData, datatype: Datatype
    ) -> dict:
        """
        Map the given TensorData to the appropriate field in InferTensorContents
        based on the provided datatype.
        :param type_object: TensorData object containing tensor values
        :param datatype: the tensor datatype
        :return: dictionary containing protobuf field name and tensor data pairs
        """
        field = _FIELDS[datatype]
        return {field: type_object}
