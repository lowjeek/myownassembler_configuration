"""Проверки разбора исходного текста."""

from pathlib import Path
import unittest

from src.assembler import parse_program
from src.isa import Instruction, Opcode


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    """Проверки синтаксиса и полей команд."""

    def test_specification_fields(self):
        """Все четыре команды дают поля из спецификации."""
        source = (ROOT / "examples/spec.asm").read_text(encoding="utf-8")
        fields = [item.describe_fields() for item in parse_program(source)]
        self.assertEqual(fields, [
            "A=127, B=921", "A=56, B=550", "A=24, B=828", "A=51",
        ])

    def test_whitespace_comments_and_case(self):
        """Регистр, пустые строки и комментарии не влияют на разбор."""
        source = "; заголовок\n\n   lOaD\t-17  ; число\n abs\n"
        self.assertEqual(parse_program(source), [
            Instruction(Opcode.LOAD, -17), Instruction(Opcode.ABS),
        ])

    def test_invalid_instructions(self):
        """Ошибки содержат номер исходной строки."""
        cases = (
            "NOOP", "LOAD", "ABS 1", "READ 1 2", "READ -1", "READ 1024",
            "WRITE -1", "WRITE 8192", "LOAD 65536", "LOAD -65537",
            "LOAD 1.5", "LOAD 1_000", "LOAD 0x01",
        )
        for command in cases:
            with self.subTest(command=command):
                with self.assertRaisesRegex(ValueError, r"строка 2:"):
                    parse_program(f"; комментарий\n{command}")
