"""Преобразование команд между двумя представлениями."""

from .isa import FORMATS, Instruction, Opcode


OPCODE_BITS = 7
BYTE_ORDER = "little"
OPCODE_MASK = (1 << OPCODE_BITS) - 1


def encode_instruction(instruction):
    """Упаковать поля A и B в байты команды."""
    layout = FORMATS[instruction.opcode]
    word = instruction.opcode.value
    if instruction.operand is not None:
        operand_mask = (1 << layout.operand_bits) - 1
        word |= (instruction.operand & operand_mask) << OPCODE_BITS
    return word.to_bytes(layout.size, BYTE_ORDER)


def decode_operand(word, layout):
    """Извлечь операнд и восстановить знак, если он предусмотрен."""
    if not layout.operand_bits:
        return None
    operand = word >> OPCODE_BITS
    if layout.signed:
        sign_bit = 1 << (layout.operand_bits - 1)
        if operand & sign_bit:
            operand -= sign_bit << 1
    return operand


def decode_instruction(code, offset):
    """Декодировать команду по смещению и вернуть следующее смещение."""
    try:
        opcode = Opcode(code[offset] & OPCODE_MASK)
    except ValueError:
        raise ValueError(f"байт {offset}: неизвестный код команды") from None
    layout = FORMATS[opcode]
    end = offset + layout.size
    if end > len(code):
        raise ValueError(f"байт {offset}: неполная команда {opcode.name}")
    word = int.from_bytes(code[offset:end], BYTE_ORDER)
    if word >> (OPCODE_BITS + layout.operand_bits):
        raise ValueError(f"байт {offset}: ненулевые зарезервированные биты")
    return Instruction(opcode, decode_operand(word, layout)), end


def format_bytes(data):
    """Представить байты как последовательность шестнадцатеричных чисел."""
    return ", ".join(f"0x{byte:02X}" for byte in data)
