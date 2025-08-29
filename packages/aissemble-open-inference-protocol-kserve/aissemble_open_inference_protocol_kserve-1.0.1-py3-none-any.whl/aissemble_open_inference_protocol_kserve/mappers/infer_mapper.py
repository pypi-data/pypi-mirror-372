###
# #%L
# aiSSEMBLE::Open Inference Protocol::KServe
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

from kserve import InferRequest, InferResponse, InferOutput
from aissemble_open_inference_protocol_shared.types.dataplane import (
    InferenceRequest,
    InferenceResponse,
    RequestInput,
    RequestOutput,
    Datatype,
    TensorData,
    Parameters,
)

from aissemble_open_inference_protocol_shared.codecs.utils import (
    get_content_type,
)


class InferMapper:
    @staticmethod
    def infer_request_to_inference_request(request: InferRequest) -> InferenceRequest:
        inference_input_list = []
        inference_output_list = []
        parameter = None
        content_type = get_content_type(request)
        if content_type is not None:
            parameter = Parameters(
                content_type=request.parameters["content_type"],
            )

        if request.inputs is not None:
            for input in request.inputs:
                input_parameter = None
                if input.parameters is not None:
                    content_type = get_content_type(input)
                    if content_type is not None:
                        input_content_type = content_type
                        input_parameter = Parameters(
                            content_type=input_content_type,
                        )

                req_input = RequestInput(
                    name=input.name,
                    shape=input.shape,
                    datatype=Datatype[input.datatype],
                    parameters=input_parameter,
                    data=TensorData(root=input.data),
                )
                inference_input_list.append(req_input)
        if request.request_outputs is not None:
            for output in request.request_outputs:
                output_parameter = None
                if output.parameters is not None:
                    content_type = get_content_type(output)
                    if content_type is not None:
                        output_parameter = Parameters(
                            content_type=output.parameters["content_type"]
                        )
                req_output = RequestOutput(
                    name=output.name, parameters=output_parameter
                )
                inference_output_list.append(req_output)
        return InferenceRequest(
            id=request.id,
            parameters=parameter,
            inputs=inference_input_list,
            outputs=inference_output_list,
        )

    @staticmethod
    def inference_response_to_infer_response(
        response: InferenceResponse,
    ) -> InferResponse:
        inference_list = []

        for output in response.outputs:
            data_list = []
            # TensorData can be represented in a form of 2D matrix or flattened 1D list, we need to take account of two use cases.
            # gRPC protocol looks for flattened data so we needed to iterate through output data and save as flattened if data is 2d.
            for initial_data_list in output.data.root:
                if isinstance(initial_data_list, list):
                    for nested_data_list in initial_data_list:
                        data_list.append(nested_data_list)
                else:
                    data_list.append(initial_data_list)

            res_output = InferOutput(
                name=output.name,
                shape=output.shape,
                datatype=output.datatype.value,
                parameters=output.parameters,
                data=data_list,
            )
            inference_list.append(res_output)
        return InferResponse(
            response_id=response.id,
            model_name=response.model_name,
            model_version=response.model_version,
            parameters=response.parameters,
            infer_outputs=inference_list,
        )
