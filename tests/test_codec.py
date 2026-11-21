"""Проверки преобразования инструкций в машинный код."""

import unittest

from src.assembler import parse_program
from src.codec import encode_instruction


class EncodingTests(unittest.TestCase):
    """Проверки байтовых последовательностей."""

    def test_specification_bytes(self):
        """Все четыре команды совпадают с байтами из спецификации."""
        cases = (
            ("LOAD 921", "FF CC 01"),
            ("READ 550", "38 13 01"),
            ("WRITE 828", "18 9E 01"),
            ("ABS", "33"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                command, = parse_program(source)
                self.assertEqual(
                    encode_instruction(command), bytes.fromhex(expected),
                )

    def test_limit_bytes(self):
        """Проверить крайние значения полей B."""
        cases = (
            ("LOAD -65536", "7F 00 80"),
            ("LOAD -1", "FF FF FF"),
            ("LOAD 65535", "FF FF 7F"),
            ("READ 1023", "B8 FF 01"),
            ("WRITE 8191", "98 FF 0F"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                command, = parse_program(source)
                self.assertEqual(
                    encode_instruction(command), bytes.fromhex(expected),
                )
