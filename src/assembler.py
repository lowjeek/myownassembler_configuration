"""Разбор текста программы и командный интерфейс ассемблера."""

import argparse
from pathlib import Path
import re

from .codec import encode_instruction, format_bytes
from .isa import FORMATS, Instruction, Opcode


DECIMAL_INTEGER = re.compile(r"[+-]?[0-9]+")
NO_OPERANDS = 0
ONE_OPERAND = 1


def parse_operand(opcode, text):
    """Преобразовать десятичный операнд и проверить границы."""
    if not DECIMAL_INTEGER.fullmatch(text):
        raise ValueError(f"ожидалось десятичное целое, получено {text!r}")
    operand = int(text, 10)
    low, high = FORMATS[opcode].operand_bounds()
    if not low <= operand <= high:
        raise ValueError(f"{opcode.name}: операнд вне диапазона {low}…{high}")
    return operand


def parse_instruction(text):
    """Разобрать непустую строку команды."""
    mnemonic, *args = text.split()
    try:
        opcode = Opcode[mnemonic.upper()]
    except KeyError:
        raise ValueError(f"неизвестная мнемоника {mnemonic!r}") from None
    expected = ONE_OPERAND if FORMATS[opcode].operand_bits else NO_OPERANDS
    if len(args) != expected:
        raise ValueError(f"{opcode.name}: ожидается операндов: {expected}")
    operand = parse_operand(opcode, args[0]) if args else None
    return Instruction(opcode, operand)


def parse_program(source):
    """Преобразовать исходный текст в список команд."""
    program = []
    for number, line in enumerate(source.splitlines(), start=1):
        text = line.partition(";")[0].strip()
        if not text:
            continue
        try:
            program.append(parse_instruction(text))
        except ValueError as error:
            raise ValueError(f"строка {number}: {error}") from error
    return program


def main(argv=None):
    """Разобрать аргументы CLI и обработать исходный файл."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ, вариант 5")
    parser.add_argument("source", type=Path, help="текст программы в UTF-8")
    parser.add_argument("output", type=Path, help="двоичный файл результата")
    parser.add_argument("--test", action="store_true", help="режим теста")
    args = parser.parse_args(argv)
    try:
        program = parse_program(args.source.read_text(encoding="utf-8"))
        chunks = [encode_instruction(command) for command in program]
        data = b"".join(chunks)
        args.output.write_bytes(data)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.test:
        for chunk in chunks:
            print(format_bytes(chunk))
    print(f"Размер двоичного файла: {len(data)} байт")


if __name__ == "__main__":
    main()
