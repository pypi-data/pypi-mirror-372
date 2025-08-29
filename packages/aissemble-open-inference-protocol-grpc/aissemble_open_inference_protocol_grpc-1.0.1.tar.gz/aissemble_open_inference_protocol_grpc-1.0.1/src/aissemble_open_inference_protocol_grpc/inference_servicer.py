###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
import grpc
from krausening.logging import LogManager

from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2 import (
    ModelInferRequest,
    ModelInferResponse,
    ModelMetadataRequest,
    ModelMetadataResponse,
    ServerMetadataResponse,
    ModelReadyResponse,
    ServerLiveResponse,
    ServerReadyResponse,
    ModelReadyRequest,
    ServerLiveRequest,
    ServerReadyRequest,
    ServerMetadataRequest,
)
from aissemble_open_inference_protocol_grpc.grpc_inference_service_pb2_grpc import (
    GrpcInferenceServiceServicer,
)
from aissemble_open_inference_protocol_grpc.mappers.model_inference_request_mapper import (
    ModelInferenceRequestMapper,
)
from aissemble_open_inference_protocol_grpc.mappers.model_inference_response_mapper import (
    ModelInferenceResponseMapper,
)
from aissemble_open_inference_protocol_grpc.mappers.model_metadata_response_mapper import (
    ModelMetadataResponseMapper,
)
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
)
from aissemble_open_inference_protocol_shared.codecs.utils import (
    build_inference_response,
)


class InferenceServicer(GrpcInferenceServiceServicer):
    logger = LogManager.get_instance().get_logger("InferenceServicer")

    def __init__(self, handler: DataplaneHandler):
        self.handler = handler

    def ModelInfer(
        self, request: ModelInferRequest, context: grpc.ServicerContext
    ) -> ModelInferResponse:
        """The ModelInfer API performs inference using the specified model. Errors are
        indicated by the google.rpc.Status returned for the request. The OK code
        indicates success and other codes indicate failure.
        """
        self.logger.info("Received Model Inference request")
        try:
            model_inference_request_mapper = ModelInferenceRequestMapper()
            inference_request = model_inference_request_mapper.to_inference_request(
                request
            )
        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to deserialize model inference request: {e}",
            )

        try:
            inference_request.validate_oip()
        except (ValueError, TypeError) as e:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Failed to validate InferenceRequest {e}",
            )

        try:
            self.logger.info("Sending model inference request to the handler")
            # Send request to handler
            handler_response = self.handler.infer(
                payload=inference_request,
                model_name=request.model_name,
                model_version=request.model_version,
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")

        try:
            handler_response.validate_oip()
        except (ValueError, TypeError) as e:
            context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to validate InferenceResponse {e}"
            )

        try:
            encoded_response = build_inference_response(
                request.model_name,
                inference_request,
                handler_response,
                request.model_version,
            )
            inference_response_mapper = ModelInferenceResponseMapper()
            return inference_response_mapper.to_model_inference_response(
                encoded_response
            )
        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to serialize inference response! {e}"
            )

    def ModelMetadata(
        self, request: ModelMetadataRequest, context
    ) -> ModelMetadataResponse:
        try:
            response = self.handler.model_metadata(request.name, request.version)
            return ModelMetadataResponseMapper.from_model_metadata_response(response)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")

    def ModelReady(self, request: ModelReadyRequest, context) -> ModelReadyResponse:
        try:
            response = self.handler.model_ready(
                model_name=request.name, model_version=request.version
            )
            return ModelReadyResponse(ready=response.ready)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")

    def ServerLive(self, request: ServerLiveRequest, context) -> ServerLiveResponse:
        try:
            response = self.handler.server_live()
            return ServerLiveResponse(live=response.live)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")

    def ServerReady(self, request: ServerReadyRequest, context) -> ServerReadyResponse:
        try:
            response = self.handler.server_ready()
            return ServerReadyResponse(ready=response.live)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")

    def ServerMetadata(
        self, request: ServerMetadataRequest, context
    ) -> ServerMetadataResponse:
        try:
            response = self.handler.server_metadata()
            return ServerMetadataResponse(
                name=response.name,
                version=response.version,
                extensions=response.extensions,
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error! {e}")
