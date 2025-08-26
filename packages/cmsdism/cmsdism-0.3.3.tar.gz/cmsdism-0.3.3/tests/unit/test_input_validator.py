from enum import Enum
from unittest.mock import MagicMock, create_autospec

import numpy as np
import pytest
from dism_core.properties.isvc.base import InferenceServiceProperties
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.types import ResourceType

from dismcli.lib.builder.input_validator import InputSignatureValidator


@pytest.fixture
def mock_dials():
    mock = MagicMock()
    mock.mes.list.return_value = [
        MagicMock(me="me1", me_id=1, dim=1),
        MagicMock(me="me2", me_id=2, dim=2),
        MagicMock(me="me3", me_id=3, dim=3),
    ]
    mock.h1d.list.return_value.results = [MagicMock(data=np.array([1, 2, 3]))]
    mock.h2d.list.return_value.results = [MagicMock(data=np.array([[1, 2], [3, 4]]))]
    return mock


@pytest.fixture
def mock_resource():
    resource = create_autospec(InferenceServiceResource, instance=True)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.Workspace = "test_workspace"
    resource.Properties = create_autospec(InferenceServiceProperties, instance=True)
    resource.Properties.InputSignature = [
        MagicMock(
            Name="input1",
            MonitoringElement="me1",
            DataType="float32",
            Dims=[-1, 3],
        ),
        MagicMock(
            Name="input2",
            MonitoringElement="me2",
            DataType="float32",
            Dims=[-1, 2, 2],
        ),
    ]
    return resource


@pytest.fixture
def mock_resource_unsupported_dim():
    resource = create_autospec(InferenceServiceResource, instance=True)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.Workspace = "test_workspace"
    resource.Properties = create_autospec(InferenceServiceProperties, instance=True)
    resource.Properties.InputSignature = [
        MagicMock(
            Name="input1",
            MonitoringElement="me3",
            DataType="float32",
            Dims=[-1, 3, 3, 51],
        )
    ]
    return resource


@pytest.fixture
def validator(mock_resource, mock_dials):
    creds = MagicMock()
    creds.client.base_url = "http://example.com"
    validator = InputSignatureValidator(mock_resource, creds)
    validator.dials = mock_dials
    return validator


def test_shape_matches():
    assert InputSignatureValidator.shape_matches((1, 2, 3), (1, 2, 3)) is True
    assert InputSignatureValidator.shape_matches((1, 2, 3), (1, -1, 3)) is True
    assert InputSignatureValidator.shape_matches((1, 2, 3), (1, 2)) is False
    assert InputSignatureValidator.shape_matches((1, 2, 3), (1, 2, 4)) is False


def test_parse_input_signature(validator):
    result = validator.parse_input_signature(validator.resource.Properties)
    assert len(result) == 2
    assert result[0]["name"] == "input1"
    assert result[0]["monitoring_element"] == "me1"
    assert result[0]["dims"] == [-1, 3]
    assert result[1]["name"] == "input2"
    assert result[1]["monitoring_element"] == "me2"
    assert result[1]["dims"] == [-1, 2, 2]


def test_parse_input_signature_invalid_me(validator):
    validator.dials.mes.list.return_value = []
    with pytest.raises(
        ValueError, match='Input signature "input1" requests the ME "me1" that is not available in DIALS.'
    ):
        validator.parse_input_signature(validator.resource.Properties)


def test_unsupported_input_dimension(mock_dials, mock_resource_unsupported_dim):
    creds = MagicMock()
    creds.client.base_url = "http://example.com"
    validator = InputSignatureValidator(mock_resource_unsupported_dim, creds)
    validator.dials = mock_dials
    signatures = validator.parse_input_signature(validator.resource.Properties)
    with pytest.raises(NotImplementedError, match="Dimension of size 3 is not supported"):
        validator.validate_input_signature(signatures)


def test_validate_input_signature(validator):
    signatures = validator.parse_input_signature(validator.resource.Properties)
    validator.validate_input_signature(signatures)


def test_validate_input_signature_invalid_shape(validator):
    validator.dials.h1d.list.return_value.results = [MagicMock(data=np.array([1, 2]))]
    signatures = validator.parse_input_signature(validator.resource.Properties)
    with pytest.raises(ValueError, match='Input signature "input1" shape \\[-1, 3\\] does not match sample data shape'):
        validator.validate_input_signature(signatures)


def test_validate(validator):
    validator.validate()


def test_validate_unsupported_resource_type(mock_resource):
    class NotImplementedResourceType(Enum):
        OTHER_SERVICE = "OtherService"

    mock_resource.SuperType = NotImplementedResourceType.OTHER_SERVICE
    creds = MagicMock()
    validator = InputSignatureValidator(mock_resource, creds)
    with pytest.raises(NotImplementedError, match="Resource super type OtherService is not supported"):
        validator.validate()
