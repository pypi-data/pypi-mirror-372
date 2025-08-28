from pathlib import Path

import eip712.model.types
from eip712.convert.input_to_resolved import EIP712InputToResolvedConverter
from eip712.convert.resolved_to_instructions import EIP712ResolvedToInstructionsConverter
from eip712.model.input.descriptor import InputEIP712DAppDescriptor
from eip712.serialize import serialize_instruction

TEST_FILE = Path(__file__).parent / "data" / "paraswap_eip712.json"
MESSAGE_INSTRUCTION = (
    "b7"  # identifier of a name mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "09"  # count of field mappers
    "4175677573747573524651204552433230206f72646572"  # name to display
)
INSTRUCTIONS_V1 = [
    # nonceAndMeta
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6e6f6e6365416e644d6574614e6f6e636520616e64206d65746164617461",  # field path and display name
    # expiry
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "65787069727945787069726174696f6e2074696d65",  # field path and display name
    # maker
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b65724d616b65722061646472657373",  # field path and display name
    # taker
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b657254616b65722061646472657373",  # field path and display name
    # makerAsset
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b657241737365744d616b657220616d6f756e74",
    # makerAmount
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b6572416d6f756e744d616b657220616d6f756e74",  # field path and display name
    # takerAsset
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b6572417373657454616b657220616d6f756e74",  # field path and display name
    # takerAmount
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b6572416d6f756e7454616b657220616d6f756e74",  # field path and display name
    # verifyingContract amount
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b6572416d6f756e74416d6f756e7420666f726d61747465642066726f6d20766572696679696e67436f6e7472616374",
]

INSTRUCTIONS_V2 = [
    # nonceAndMeta
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6e6f6e6365416e644d6574614e6f6e636520616e64206d65746164617461",  # field path and display name
    # expiry
    "48"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "65787069727945787069726174696f6e2074696d65",  # field path and  display name
    # maker
    "2c"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b65724d616b65722061646472657373"  # field path and display name
    "020201",  # name types and name sources
    # taker
    "2c"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b657254616b65722061646472657373"  # field path and display name
    "020201",  # name types and name sources
    # makerAsset
    "0b"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b6572417373657400",  # field path and token index
    # makerAmount
    "16"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b6572416d6f756e744d616b657220616d6f756e7400",  # field path, display name and token index
    # takerAsset
    "0b"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b6572417373657401",  # field path and token index
    # takerAmount
    "16"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "74616b6572416d6f756e7454616b657220616d6f756e7401",  # field path, display name and token index
    # verifyingContract amount
    "16"  # identifier of a field mapper
    "0000000000000089"  # chain id
    "f3cd476c3c4d3ac5ca2724767f269070ca09a043"  # contract address
    "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"  # message schema hash
    "6d616b6572416d6f756e74416d6f756e7420666f726d61747465642066726f6d20766572696679696e67436f6e7472616374ff",
]


def test_serialize_paraswap_instructions() -> None:
    input_model = InputEIP712DAppDescriptor.load(TEST_FILE)
    resolved_model = EIP712InputToResolvedConverter().convert(input_model)
    instructions = EIP712ResolvedToInstructionsConverter().convert(resolved_model)

    serialized_instructions_v1: list[str] = []
    serialized_instructions_v2: list[str] = []
    for _, per_address in instructions.items():
        for _, instructions_list in per_address.items():
            for instruction in instructions_list:
                instruction_v1 = serialize_instruction(instruction, eip712.model.types.EIP712Version.V1)
                if instruction_v1 is not None:
                    serialized_instructions_v1.append(instruction_v1)

                instruction_v2 = serialize_instruction(instruction, eip712.model.types.EIP712Version.V2)
                if instruction_v2 is not None:
                    serialized_instructions_v2.append(instruction_v2)

    assert serialized_instructions_v1[0] == MESSAGE_INSTRUCTION
    assert serialized_instructions_v1[1:] == INSTRUCTIONS_V1

    assert serialized_instructions_v2[0] == MESSAGE_INSTRUCTION
    assert serialized_instructions_v2[1:] == INSTRUCTIONS_V2
