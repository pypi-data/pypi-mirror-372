from pathlib import Path

import eip712.model.types
from eip712.convert.input_to_resolved import EIP712InputToResolvedConverter
from eip712.convert.resolved_to_instructions import EIP712ResolvedToInstructionsConverter
from eip712.model.input.descriptor import InputEIP712DAppDescriptor
from eip712.serialize import serialize_instruction

TEST_FILE = Path(__file__).parent / "data" / "safe_eip712.json"
MESSAGE_INSTRUCTION = (
    "b7"  # identifier of a name mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "08"  # count of field mappers
    "45786563757465207472616e73616374696f6e"  # name to display
)
INSTRUCTIONS_V1 = [
    # Transaction - value
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "646174615472616e73616374696f6e",  # field path and display name
    # Transaction - callee
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "746f5472616e73616374696f6e",  # field path and display name
    # Transaction - amount
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "76616c75655472616e73616374696f6e",  # field path and display name
    # operation
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6f7065726174696f6e4f7065726174696f6e",  # field path and display name
    # baseGas
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6261736547617347617320616d6f756e74",  # field path and display name
    # gasPriceAsset
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "676173546f6b656e476173207072696365",  # field path  and display name
    # gasPriceAmount
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6761735072696365476173207072696365",  # field path and display name
    # refundReceiver
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "726566756e645265636569766572476173207265636569766572",  # field path and display name
]

INSTRUCTIONS_V2 = [
    # Transaction
    # calldata info not serialized in v1
    "37"  # calldata info
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "00010100000102",  # calldata_index and calldata_info_flags
    # Transaction - value
    "42"  # calldata value
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6461746100",  # field path and calldata_index
    # Transaction - callee
    "4d"  # calldata callee
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "746f00",  # field path and calldata_index
    # Transaction - amount
    "6e"  #  calldata amount
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "76616c756500",  # field path and calldata_index
    # operation
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6f7065726174696f6e4f7065726174696f6e",  # field path and display name
    # baseGas
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "6261736547617347617320616d6f756e74",  # field path and display name
    # gasPriceAsset
    "0b"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "676173546f6b656e00",  # field path and token index
    # gasPriceAmount
    "16"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "676173507269636547617320707269636500",  # field path, display name and token index
    # refundReceiver
    "48"  # identifier of a field mapper
    "0000000000000001"  # chain id
    "3e5c63644e683549055b9be8653de26e0b4cd36e"  # contract address
    "76c51ae1c9c8eb1e9fe51d0ed8b1c65c044466a7bcb1c9f7a0f33c14"  # message schema hash
    "726566756e645265636569766572476173207265636569766572",  # field path and display name
]


def test_serialize_safe_instructions() -> None:
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
