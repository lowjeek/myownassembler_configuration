"""Модель памяти и цикл выполнения команд УВМ."""

from .codec import decode_instruction
from .isa import FORMATS, Opcode


FIRST_ADDRESS = 0
ADDRESS_BITS = FORMATS[Opcode.WRITE].operand_bits
MEMORY_SIZE = 1 << ADDRESS_BITS


def check_address(address):
    """Проверить границы адресного пространства памяти данных."""
    if not FIRST_ADDRESS <= address < MEMORY_SIZE:
        raise ValueError(f"адрес памяти вне диапазона: {address}")


class VirtualMachine:
    """УВМ с байтовым кодом, памятью данных и аккумулятором."""

    def __init__(self):
        """Создать машину с нулевым начальным состоянием."""
        self.accumulator = 0
        self.memory = [0] * MEMORY_SIZE

    def read(self, address):
        """Прочитать значение ячейки данных."""
        check_address(address)
        return self.memory[address]

    def write(self, address, value):
        """Записать значение в ячейку данных."""
        check_address(address)
        self.memory[address] = value

    def execute(self, instruction):
        """Выполнить одну команду в промежуточном представлении."""
        opcode = instruction.opcode
        operand = instruction.operand
        if opcode is Opcode.LOAD:
            self.accumulator = operand
        elif opcode is Opcode.READ:
            self.accumulator = self.read(self.accumulator + operand)
        elif opcode is Opcode.WRITE:
            self.write(operand, self.accumulator)
        else:
            raise ValueError(f"команда {opcode.name} пока не реализована")

    def run(self, code):
        """Декодировать и выполнить все команды из отдельной памяти кода."""
        offset = 0
        while offset < len(code):
            instruction, next_offset = decode_instruction(code, offset)
            try:
                self.execute(instruction)
            except ValueError as error:
                raise ValueError(f"байт {offset}: {error}") from error
            offset = next_offset

    def dump(self, start, end):
        """Вернуть значения в заданном включительном диапазоне адресов."""
        check_address(start)
        check_address(end)
        if start > end:
            raise ValueError("начальный адрес должен быть не больше конечного")
        return {str(address): self.memory[address]
                for address in range(start, end + 1)}
