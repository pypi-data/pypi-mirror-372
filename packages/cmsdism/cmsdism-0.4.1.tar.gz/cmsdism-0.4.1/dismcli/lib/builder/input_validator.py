from typing import Union

import numpy as np
from cmsdials import Dials
from cmsdials.auth.bearer import Credentials
from cmsdials.filters import LumisectionHistogram1DFilters, LumisectionHistogram2DFilters
from dism_core.properties.isvc.base import InferenceServiceProperties
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.types import ResourceType


class InputSignatureValidator:
    def __init__(self, resource: InferenceServiceResource, dials_creds: Credentials) -> None:
        self.resource = resource
        self.dials = Dials(dials_creds, resource.Workspace, base_url=dials_creds.client.base_url)

    @staticmethod
    def shape_matches(arr_shape: Union[list, tuple], test_shape: Union[list, tuple]) -> bool:
        if isinstance(arr_shape, list):
            arr_shape = tuple(arr_shape)

        if isinstance(test_shape, list):
            test_shape = tuple(test_shape)

        # Check if number of dimensions matches
        if len(arr_shape) != len(test_shape):
            return False

        # Check each dimension
        for actual_dim, test_dim in zip(arr_shape, test_shape):
            if test_dim == -1:
                continue  # Dynamic dimension - any size is acceptable
            if actual_dim != test_dim:
                return False

        return True

    def parse_input_signature(self, props: InferenceServiceProperties) -> list[dict]:
        all_mes = self.dials.mes.list()
        input_signatures = []
        for sig in props.InputSignature:
            found_it = False
            for me in all_mes:
                if sig.MonitoringElement == me.me:
                    found_it = True
                    input_signatures.append(
                        {
                            "name": sig.Name,
                            "monitoring_element": me.me,
                            "monitoring_element_id": me.me_id,
                            "monitoring_element_dim": me.dim,
                            "data_type": sig.DataType,
                            "dims": sig.Dims,
                        }
                    )

            if found_it is False:
                raise ValueError(
                    f'Input signature "{sig.Name}" requests the ME "{sig.MonitoringElement}" that is not available in DIALS.'
                )

        return input_signatures

    def validate_input_signature(self, signatures: list[dict]) -> None:
        for sig in signatures:
            if sig["monitoring_element_dim"] == 1:
                sample = self.dials.h1d.list(LumisectionHistogram1DFilters(me_id=sig["monitoring_element_id"]))
            elif sig["monitoring_element_dim"] == 2:
                sample = self.dials.h2d.list(LumisectionHistogram2DFilters(me_id=sig["monitoring_element_id"]))
            else:
                raise NotImplementedError(f"Dimension of size {sig['monitoring_element_dim']} is not supported")
            sample = np.array([res.data for res in sample.results])
            if InputSignatureValidator.shape_matches(sample.shape, sig["dims"]) is False:
                raise ValueError(
                    f'Input signature "{sig["name"]}" shape {sig["dims"]} does not match sample data shape {sample.shape} for ME "{sig["monitoring_element"]}"'
                )

    def validate(self) -> None:
        if self.resource.SuperType == ResourceType.INFERENCE_SERVICE:
            isignatures = self.parse_input_signature(self.resource.Properties)
            self.validate_input_signature(isignatures)
        else:
            raise NotImplementedError(f"Resource super type {self.resource.SuperType.value} is not supported")
