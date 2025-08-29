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
    ModelInferRequest,
    InferParameter,
    InferTensorContents,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceRequest,
    RequestInput,
    RequestOutput,
    Parameters,
    TensorData,
    Datatype,
)


class ModelInferenceRequestMapper:
    def to_inference_request(self, request: ModelInferRequest) -> InferenceRequest:
        """
        Maps gRPC Model Inference Request to an Inference Request object.
        :param request: the model inference request
        :return: an equivalent Inference Request object
        """
        return InferenceRequest(
            id=request.id,
            parameters=self._params_to_inference_request(request.parameters),
            inputs=[
                self._input_to_inference_request(model_infer_inputs=model_infer_inputs)
                for model_infer_inputs in request.inputs
            ],
            outputs=[
                self._outputs_to_inference_outputs(
                    model_infer_outputs=model_infer_outputs
                )
                for model_infer_outputs in request.outputs
            ],
        )

    def _input_to_inference_request(
        self, model_infer_inputs: ModelInferRequest.InferInputTensor
    ) -> RequestInput:
        """
        Maps model inference request tensor data to an Inference Request tensor data object.
        :param model_infer_inputs: model inference tensor data
        :return: Inference request tensor data object
        """
        return RequestInput(
            name=model_infer_inputs.name,
            shape=model_infer_inputs.shape,
            datatype=Datatype[model_infer_inputs.datatype].value,
            parameters=self._params_to_inference_request(model_infer_inputs.parameters),
            data=self._infer_tensor_contents_to_data(model_infer_inputs.contents),
        )

    def _infer_tensor_contents_to_data(
        self, tensor_contents: InferTensorContents
    ) -> TensorData:
        """
        Maps ModelInferTensorContents to InferenceRequest compatible TensorData
        :param tensor_contents: content to map. Comes in with format - type_contents: [Any]
        :return: Mapped TensorData with format - root=Union[List[Any], Any]
        """
        contents = self._extract_contents(tensor_contents)
        return TensorData(root=list(contents))

    def _outputs_to_inference_outputs(
        self, model_infer_outputs: ModelInferRequest.InferRequestedOutputTensor
    ) -> RequestOutput:
        """
        Maps Model Inference Request outputs to an Inference Request RequestOutput object.
        :param model_infer_outputs: the model inference requested outputs
        :return: A mapped InferenceRequest RequestOutput object
        """
        return RequestOutput(
            name=model_infer_outputs.name,
            parameters=self._params_to_inference_request(
                model_infer_outputs.parameters
            ),
        )

    def _params_to_inference_request(
        self, model_infer_params: Mapping[str, InferParameter]
    ) -> Parameters:
        """
        Maps model parameters to inference request parameters.
        :param model_infer_params: the list of params in format - 'key' : type : value
        :return: InferenceRequest Parameters object in format - 'key' : value
        """
        parameters = {
            param: self._extract_contents(infer_parameter)
            for param, infer_parameter in model_infer_params.items()
        }
        return Parameters(**parameters)

    def _extract_contents(self, contents):
        fields = contents.ListFields()
        field_descriptor, field_value = fields[0]
        return field_value
