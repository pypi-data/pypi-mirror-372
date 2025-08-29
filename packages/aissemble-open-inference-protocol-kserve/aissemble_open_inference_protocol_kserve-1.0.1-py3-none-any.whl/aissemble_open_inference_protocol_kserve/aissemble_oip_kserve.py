###
# #%L
# aiSSEMBLE::Open Inference Protocol::KServe
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from kserve import Model, InferRequest, InferResponse, ModelServer

from aissemble_open_inference_protocol_kserve.mappers.infer_mapper import InferMapper
from aissemble_open_inference_protocol_shared.aissemble_oip_service import (
    AissembleOIPService,
)
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
    DefaultHandler,
)


class AissembleOIPKServe(Model, AissembleOIPService):
    def __init__(self, name: str, handler: DataplaneHandler = DefaultHandler()):
        Model.__init__(self, name)
        AissembleOIPService.__init__(self, handler=handler, adapter=None)
        self.model = None

    def predict(
        self,
        payload: InferRequest,
        headers: dict[str, str] = None,
        response_headers: dict[str, str] = None,
    ) -> InferResponse:
        inference_request = InferMapper.infer_request_to_inference_request(payload)
        inference_response = self.handler.infer(
            self,
            payload=inference_request,
            model_name=payload.model_name,
            model_version=payload.model_version,
        )

        infer_response = InferMapper.inference_response_to_infer_response(
            inference_response
        )
        return infer_response

    def load(self):
        """As loading model is different for each client, it is up to user to implement load based on their use case.
        NOTE: setting self.ready to True indicates KServe Model is ready to serve."""
        self.ready = True
        return self.ready

    async def start(self):
        self.load()
        ModelServer().start([self])
