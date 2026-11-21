"""Кодирование команд УВМ в машинное представление."""

from .isa import FORMATS


OPCODE_BITS = 7
BYTE_ORDER = "little"


def encode_instruction(instruction):
    """Упаковать поля A и B в байты команды."""
    layout = FORMATS[instruction.opcode]
    word = instruction.opcode.value
    if instruction.operand is not None:
        operand_mask = (1 << layout.operand_bits) - 1
        word |= (instruction.operand & operand_mask) << OPCODE_BITS
    return word.to_bytes(layout.size, BYTE_ORDER)


def format_bytes(data):
    """Представить байты как последовательность шестнадцатеричных чисел."""
    return ", ".join(f"0x{byte:02X}" for byte in data)
