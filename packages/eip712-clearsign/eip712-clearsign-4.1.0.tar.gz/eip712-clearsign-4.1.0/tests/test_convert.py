from pathlib import Path

import pytest

from eip712.convert.input_to_resolved import EIP712InputToResolvedConverter
from eip712.convert.resolved_to_instructions import EIP712ResolvedToInstructionsConverter
from eip712.model.input.descriptor import InputEIP712DAppDescriptor
from eip712.model.instruction import (
    EIP712CalldataInfoInstruction,
    EIP712CalldataParamPresence,
    EIP712MessageInstruction,
)
from eip712.model.resolved.descriptor import ResolvedEIP712DAppDescriptor

DATA_DIRECTORY = Path(__file__).parent / "data"


@pytest.mark.parametrize("file", ["paraswap_eip712", "safe_eip712"])
def test_convert(file: str) -> None:
    input_model = InputEIP712DAppDescriptor.load(DATA_DIRECTORY / f"{file}.json")
    resolved_model = EIP712InputToResolvedConverter().convert(input_model)

    resolved_expected_model = ResolvedEIP712DAppDescriptor.load(DATA_DIRECTORY / f"{file}.resolved.json")

    assert resolved_model == resolved_expected_model


def test_instructions_paraswap() -> None:
    input_model = InputEIP712DAppDescriptor.load(DATA_DIRECTORY / "paraswap_eip712.json")
    resolved_model = EIP712InputToResolvedConverter().convert(input_model)
    instructions = EIP712ResolvedToInstructionsConverter().convert(resolved_model)

    assert len(instructions) == 1
    assert "0xf3cd476c3c4d3ac5ca2724767f269070ca09a043" in instructions
    dict_for_address = instructions["0xf3cd476c3c4d3ac5ca2724767f269070ca09a043"]
    assert len(dict_for_address) == 1
    assert "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3" in dict_for_address
    instructions_list = dict_for_address["16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"]
    assert len(instructions_list) == 10

    message = instructions_list[0]
    assert isinstance(message, EIP712MessageInstruction)

    assert message.display_name == "AugustusRFQ ERC20 order"
    assert message.field_mappers_count == 9


def test_instructions_safe() -> None:
    input_model = InputEIP712DAppDescriptor.load(DATA_DIRECTORY / "safe_eip712.json")
    resolved_model = EIP712InputToResolvedConverter().convert(input_model)
    instructions = EIP712ResolvedToInstructionsConverter().convert(resolved_model)

    assert len(instructions) == 1
    assert "0x3e5c63644e683549055b9be8653de26e0b4cd36e" in instructions
    dict_for_address = instructions["0x3e5c63644e683549055b9be8653de26e0b4cd36e"]
    assert len(dict_for_address) == 1
    assert "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14" in dict_for_address
    instructions_list = dict_for_address["76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"]
    assert len(instructions_list) == 10

    message = instructions_list[0]
    assert isinstance(message, EIP712MessageInstruction)

    assert message.display_name == "Execute transaction"
    assert message.field_mappers_count == 8  # EIP712CalldataInfoInstruction not included

    calldata_info = instructions_list[1]
    assert isinstance(calldata_info, EIP712CalldataInfoInstruction)
    assert calldata_info.calldata_index == 0
    assert calldata_info.value_filter_flag is True
    assert calldata_info.callee_filter_flag is EIP712CalldataParamPresence.PRESENT
    assert calldata_info.chain_id_filter_flag is False
    assert calldata_info.selector_filter_flag is False
    assert calldata_info.amount_filter_flag is True
    assert calldata_info.spender_filter_flag is EIP712CalldataParamPresence.VERIFYING_CONTRACT
