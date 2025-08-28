import pytest

from eip712.model.schema import EIP712SchemaField, EIP712Type
from eip712.utils import MissingRootTypeError, MultipleRootTypesError, get_primary_type


def test_get_primary_type() -> None:
    schema = {
        "Asset": [
            EIP712SchemaField(name="assetTypes", type="AssetType[]"),
            EIP712SchemaField(name="value", type="uint256"),
        ],
        "AssetType": [
            EIP712SchemaField(name="assetClass", type="bytes4"),
            EIP712SchemaField(name="data", type="bytes"),
        ],
        "EIP712Domain": [
            EIP712SchemaField(name="name", type="string"),
            EIP712SchemaField(name="version", type="string"),
            EIP712SchemaField(name="chainId", type="uint256"),
            EIP712SchemaField(name="verifyingContract", type="address"),
        ],
        "Order": [
            EIP712SchemaField(name="maker", type="address"),
            EIP712SchemaField(name="makeAsset", type="Asset"),
        ],
    }
    assert get_primary_type(schema) == "Order"


def test_get_primary_type_missing_root() -> None:
    schema = {
        "A": [
            EIP712SchemaField(name="b", type="B"),
        ],
        "B": [
            EIP712SchemaField(name="c", type="C"),
        ],
        "C": [
            EIP712SchemaField(name="a", type="A"),
        ],
    }
    with pytest.raises(MissingRootTypeError):
        get_primary_type(schema)


def test_get_primary_type_multiple_roots() -> None:
    schema: dict[EIP712Type, list[EIP712SchemaField]] = {
        "A": [],
        "B": [],
    }
    with pytest.raises(MultipleRootTypesError):
        get_primary_type(schema)
