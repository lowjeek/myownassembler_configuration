"""Проверки выполнения программ и границ памяти УВМ."""

from pathlib import Path
import unittest

from src.assembler import parse_program
from src.codec import encode_instruction
from src.vm import VirtualMachine


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def run_example(name):
    """Ассемблировать и выполнить пример в новой виртуальной машине."""
    source = (EXAMPLES / name).read_text(encoding="utf-8")
    program = parse_program(source)
    code = b"".join(encode_instruction(item) for item in program)
    machine = VirtualMachine()
    machine.run(code)
    return machine


class MachineTests(unittest.TestCase):
    """Проверки памяти данных и выполнения команд."""

    def test_copy(self):
        """READ с ненулевым смещением сохраняет правильный порядок."""
        machine = run_example("copy.asm")
        self.assertEqual(machine.dump(200, 202), {
            "200": 9, "201": -4, "202": 12,
        })
        self.assertEqual(machine.dump(100, 102), {
            "100": 9, "101": -4, "102": 12,
        })

    def test_uninitialized_and_boundary_cells(self):
        """Дамп включает границы, а начальная память заполнена нулями."""
        machine = VirtualMachine()
        machine.run(bytes.fromhex("FF 00 00 98 FF 0F"))
        self.assertEqual(machine.dump(0, 0), {"0": 0})
        self.assertEqual(machine.dump(8191, 8191), {"8191": 1})

    def test_invalid_memory_access(self):
        """Отрицательные и слишком большие эффективные адреса отклоняются."""
        examples = ("FF FF FF 38 00 00", "7F 00 10 38 00 00")
        for code in examples:
            with self.subTest(code=code):
                with self.assertRaisesRegex(ValueError, r"байт 3: адрес"):
                    VirtualMachine().run(bytes.fromhex(code))

    def test_invalid_dump_range(self):
        """Отклонить обратный порядок и адреса вне памяти."""
        machine = VirtualMachine()
        for start, end in ((3, 2), (-1, 2), (8191, 8192)):
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    machine.dump(start, end)

    def test_abs_of_minimum_literal(self):
        """Модуль минимальной константы доходит до памяти как 65536."""
        machine = run_example("abs.asm")
        self.assertEqual(machine.dump(30, 31), {"30": -65536, "31": 65536})

    def test_abs_uses_accumulator_as_address(self):
        """При ABS проверяется адрес операнда, хранящийся в аккумуляторе."""
        with self.assertRaisesRegex(ValueError, r"байт 3: адрес"):
            VirtualMachine().run(bytes.fromhex("FF FF FF 33"))
