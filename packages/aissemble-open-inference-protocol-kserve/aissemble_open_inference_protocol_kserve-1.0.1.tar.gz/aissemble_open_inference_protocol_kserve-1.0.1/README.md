# aiSSEMBLE Open Inference Protocol&trade; KServe

The [Open Inference Protocol (OIP)](https://github.com/kserve/open-inference-protocol) specification defines a standard protocol for performing machine learning model inference across serving runtimes for different ML frameworks. This Python application can be leveraged to deploy KServe that are compatible with the Open Inference Protocol.

## Installation
Add `aissemble-open-inference-protocol-kserve` to an application
```bash
pip install aissemble-open-inference-protocol-kserve
```

## Implementing a Handler
To make a custom handler to integrate with kserve, create your class and extend the [AissembleOIPKServe](https://github.com/boozallen/aissemble-open-inference-protocol/blob/dev/aissemble-open-inference-protocol-kserve/src/aissemble_open_inference_protocol_kserve/aissemble_oip_kserve.py).
Then, implement methods based on the model such as load() for loading a model, and optional preprocess() and/or postprocess() for transforming input or output data for client and prediction model.
predict method will call infer method of dataplaneHandler in which you need to implement either with [REST](../aissemble-open-inference-protocol-fastapi/README.md) or [gRPC](../aissemble-open-inference-protocol-grpc/README.md)

### Example of Usage with a Handler
Create your custom handler class with:
```python
from kserve import ModelServer
from aissemble_open_inference_protocol_kserve.aissemble_oip_kserve import (
    AissembleOIPKServe,
)

class KserveCustomHandler(AissembleOIPKServe):
    """
    Implements Custom predictor of AissembleOIPKServe for requesting model.
    handler refers to custom DataplaneHandler
    """
    def __init__(self, name: str, model_path: str, handler=None):
        super().__init__(name, handler)
        self.model = None
        self.name = name
        self.model_path = model_path
        self.handler = handler

    def preprocess(self):
        """As preprocess is optional API in KServe, it is up to user to implement preprocess based on their use case to transform raw input to the format expected for model serve if applicable."""
    pass
    
    def postprocess(self):
        """As postprocess is optional API in KServe, it is up to user to implement preprocess based on their use case to transform prediction output to the format expected for client if applicable."""
        pass

    def load(self):
        """As loading model is different for each client, it is up to user to implement load based on their use case. 
        NOTE: setting self.ready to True will make sure KServe Model is ready to serve."""
        self.ready = True
        return self.ready

    async def start(self):
        self.load()
        ModelServer().start([self])

if __name__ == "__main__":
    # DataplaneHandler is abstract base class, user should be extending this class for their implementation based on preferred API calls (REST or GRPC)
    model = KserveCustomHandler( name= "sample_model",
        model_path="sample_model_path",
        handler=DataplaneHandler,
    )
    model.load()
    model.start()
```

Once you built your custom image for python application for KServe and KServe setup is complete, then you can run prediction based on preferred API calls (REST or gRPC)

## Examples
For working examples, refer to the [Examples](https://github.com/boozallen/aissemble-open-inference-protocol/blob/dev/aissemble-open-inference-protocol-examples/README.md#kserve) documentation.