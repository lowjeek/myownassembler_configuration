"""Проверки преобразования инструкций в машинный код."""

import unittest

from src.assembler import parse_program
from src.codec import decode_instruction, encode_instruction


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


class DecodingTests(unittest.TestCase):
    """Проверки загрузки корректного и повреждённого кода."""

    def test_decode_mixed_sizes_and_signed_operand(self):
        """Последовательно прочитать короткую и длинную команды."""
        code = bytes.fromhex("33 7F 00 80 38 13 01")
        absolute, offset = decode_instruction(code, 0)
        load, offset = decode_instruction(code, offset)
        read, offset = decode_instruction(code, offset)
        self.assertEqual([absolute, load, read],
                         parse_program("ABS\nLOAD -65536\nREAD 550"))
        self.assertEqual(offset, len(code))

    def test_invalid_machine_code(self):
        """Проверить неизвестный opcode, обрезание и биты заполнения."""
        cases = (
            ("00", "неизвестный код"),
            ("FF CC", "неполная команда"),
            ("38 13 03", "зарезервированные биты"),
            ("18 9E 11", "зарезервированные биты"),
            ("B3", "зарезервированные биты"),
        )
        for encoded, message in cases:
            with self.subTest(encoded=encoded):
                with self.assertRaisesRegex(ValueError, message):
                    decode_instruction(bytes.fromhex(encoded), 0)
