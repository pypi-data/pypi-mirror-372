from typing import List, Optional, Tuple

import joblib
import numpy as np
from datatype import dtype_to_datatype
from mlserver import MLModel
from mlserver.types import InferenceRequest, InferenceResponse, RequestInput, RequestOutput, ResponseOutput
from mlserver.utils import get_model_uri
from nmf_regressor import NMFRegressor, Preprocessing

import __main__


# When joblib tries to load our model it will look in the module name the was dumped
# for custom objects needed by our model. Since our model was dumped from a jupyter notebook
# the default module named used is __main__.
# Our model is a scikit-learn Pipeline of Preprocessing -> NMFRegressor
# So we need both custom definitions during runtime in __main__.
__main__.Preprocessing = Preprocessing
__main__.NMFRegressor = NMFRegressor


class Handler(MLModel):
    async def load(self):
        model_uri = await get_model_uri(self._settings)
        self.model_name = self._settings.name
        self.model_version = self._settings.version
        self.model = joblib.load(model_uri)

    async def preprocess(self, inputs: List[RequestInput]) -> np.ndarray:
        """Process data sent from HTTP request"""
        # input_datatype = datatype_to_dtype(inputs[0].datatype)
        input_shape = tuple(inputs[0].shape)
        input_data = np.array(
            inputs[0].data, dtype=np.float64
        )  # Ignore the original datatype, since this model requires float64
        if input_data.shape != input_shape:
            input_data = input_data.flatten().reshape(input_shape)
        return input_data

    async def inference(self, preprocessed_data: np.ndarray) -> Tuple[np.ndarray]:
        """Run inference"""
        reconstructed, avg_mse = self.model.predict(preprocessed_data)
        return reconstructed, avg_mse

    async def postprocess(
        self, outputs: Optional[List[RequestOutput]], results: Tuple[np.ndarray]
    ) -> List[ResponseOutput]:
        """Process results from model inference and make each output compliant with Open Inference Protocol"""
        if outputs is None:
            output_names = [f"output_{idx}" for idx in range(len(results))]
        else:
            output_names = [output.name for output in outputs]

        _outputs = []
        for idx, result in enumerate(results):
            _outputs.append(
                ResponseOutput(
                    name=output_names[idx],
                    shape=result.shape,
                    datatype=dtype_to_datatype(result.dtype),
                    data=result.flatten().tolist(),
                )
            )

        return _outputs

    async def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Main handler called on each inference HTTP request at /infer

        Variables are overwritten to free memory, since in this specific case
        data from older steps are not usable in later steps.

        The output is compliant with Open Inference Protocol.
        """
        data = await self.preprocess(request.inputs)  # pre-processed data
        data = await self.inference(data)  # model results
        data = await self.postprocess(request.outputs, data)  # post-processed outputs compliant to OIP
        return InferenceResponse(
            id=request.id, model_name=self.model_name, model_version=self.model_version, outputs=data
        )
