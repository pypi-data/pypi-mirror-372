from typing import List, Optional, Tuple

import numpy as np
from datatype import datatype_to_dtype, dtype_to_datatype
from mlserver import MLModel
from mlserver.types import InferenceRequest, InferenceResponse, RequestInput, RequestOutput, ResponseOutput
from mlserver.utils import get_model_uri
from sklearn.preprocessing import MinMaxScaler

import xgboost as xgb


class Handler(MLModel):
    async def load(self):
        model_uri = await get_model_uri(self._settings)
        self.model_name = self._settings.name
        self.model_version = self._settings.version
        self.model = xgb.Booster(model_file=model_uri)

    async def preprocess(self, inputs: List[RequestInput]) -> np.ndarray:
        """Process data sent from HTTP request"""
        input_datatype = datatype_to_dtype(inputs[0].datatype)
        input_shape = tuple(inputs[0].shape)
        input_data = np.array(inputs[0].data, dtype=input_datatype)
        if input_data.shape != input_shape:
            input_data = input_data.flatten().reshape(input_shape)
        return MinMaxScaler().fit_transform(input_data)

    async def inference(self, preprocessed_data: np.ndarray) -> Tuple[np.ndarray]:
        """Run inference"""
        dmatrix = xgb.DMatrix(preprocessed_data)
        reconstructed = self.model.predict(dmatrix)
        avg_mse: np.ndarray = np.mean((preprocessed_data - reconstructed) ** 2, axis=1)
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
