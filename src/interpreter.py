"""Командный интерфейс интерпретатора УВМ."""

import argparse
import json
from pathlib import Path

from .vm import VirtualMachine


def main(argv=None):
    """Прочитать код, выполнить программу и записать JSON-дамп."""
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ")
    parser.add_argument("binary", type=Path, help="двоичный файл программы")
    parser.add_argument("output", type=Path, help="выходной JSON-дамп")
    parser.add_argument("start", type=int, help="начальный адрес")
    parser.add_argument("end", type=int, help="конечный адрес (включительно)")
    args = parser.parse_args(argv)
    try:
        machine = VirtualMachine()
        machine.run(args.binary.read_bytes())
        dump = machine.dump(args.start, args.end)
        args.output.write_text(json.dumps(dump, indent=2) + "\n",
                               encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
