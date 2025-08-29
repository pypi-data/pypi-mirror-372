###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2 import (
    ModelMetadataResponse,
)
from aissemble_open_inference_protocol_shared.types.dataplane import (
    ModelMetadataResponse as ModelMetadataResponseType,
    MetadataTensor,
)


class ModelMetadataResponseMapper:
    """
    Class used to map handler model metadata response to the gRPC model metadata response.
    """

    @staticmethod
    def from_model_metadata_response(
        response: ModelMetadataResponseType,
    ) -> ModelMetadataResponse:
        """
        Maps the handlers model metadata response to the gRPC equivalent
        Args:
            response: The handlers model metadata response

        Returns: the gRPC equivalent model metadata response
        """
        return ModelMetadataResponse(
            name=response.name,
            versions=response.versions,
            platform=response.platform,
            inputs=[
                ModelMetadataResponseMapper.from_metadata_tensor(inputs)
                for inputs in response.inputs
            ],
            outputs=[
                ModelMetadataResponseMapper.from_metadata_tensor(outputs)
                for outputs in response.outputs
            ],
        )

    @staticmethod
    def from_metadata_tensor(
        metadata_tensor: MetadataTensor,
    ) -> ModelMetadataResponse.TensorMetadata:
        return ModelMetadataResponse.TensorMetadata(
            name=metadata_tensor.name,
            datatype=metadata_tensor.datatype.value,
            shape=metadata_tensor.shape,
        )
