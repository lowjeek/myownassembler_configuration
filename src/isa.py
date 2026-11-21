"""Поля и форматы команд УВМ."""

from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """Значения поля A для поддерживаемых команд."""

    LOAD = 127
    READ = 56
    WRITE = 24
    ABS = 51


@dataclass(frozen=True)
class CommandFormat:
    """Размер команды и представление её операнда."""

    size: int
    operand_bits: int = 0
    signed: bool = False

    def operand_bounds(self):
        """Вернуть допустимые границы для операнда."""
        if self.signed:
            half = 1 << (self.operand_bits - 1)
            return -half, half - 1
        return 0, (1 << self.operand_bits) - 1


FORMATS = {
    Opcode.LOAD: CommandFormat(3, 17, signed=True),
    Opcode.READ: CommandFormat(3, 10),
    Opcode.WRITE: CommandFormat(3, 13),
    Opcode.ABS: CommandFormat(1),
}


@dataclass(frozen=True)
class Instruction:
    """Команда в промежуточном представлении."""

    opcode: Opcode
    operand: int | None = None

    def describe_fields(self):
        """Представить значения полей команды в текстовом виде."""
        fields = f"A={self.opcode.value}"
        if self.operand is not None:
            fields += f", B={self.operand}"
        return fields
