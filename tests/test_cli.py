"""Сквозные проверки командной строки ассемблера и интерпретатора."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "run.sh"


def invoke(*args):
    """Запустить проект через скрипт из корня репозитория."""
    return subprocess.run(
        [RUN, *args], cwd=ROOT, check=True, capture_output=True,
        encoding="utf-8",
    ).stdout


class CommandLineTests(unittest.TestCase):
    """Проверки записанных файлов и вывода на экран."""

    def test_specification_listing_and_binary(self):
        """Сравнить весь вывод тестового режима и выходной файл."""
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "example.bin"
            listing = invoke("assemble", "examples/spec.asm", binary, "--test")
            self.assertEqual(binary.read_bytes(),
                             bytes.fromhex("FF CC 01 38 13 01 18 9E 01 33"))
        self.assertEqual(listing.splitlines(), [
            "0xFF, 0xCC, 0x01", "0x38, 0x13, 0x01",
            "0x18, 0x9E, 0x01", "0x33", "Размер двоичного файла: 10 байт",
        ])

    def test_vector_dumps(self):
        """Проверить три пары векторов в JSON после запуска обеих CLI."""
        cases = (
            ("mixed", [-8, 0, 3, -21, 7, -1, 12], [8, 0, 3, 21, 7, 1, 12]),
            ("negative", [-2, -4, -6, -8, -10, -12, -14],
             [2, 4, 6, 8, 10, 12, 14]),
            ("boundary", [-65536, 65535, -32768, 0, 1, -1, -65535],
             [65536, 65535, 32768, 0, 1, 1, 65535]),
        )
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "vector.bin"
            dump_file = Path(directory) / "vector.json"
            for name, original, expected in cases:
                with self.subTest(name=name):
                    invoke("assemble", f"examples/vector_{name}.asm", binary)
                    invoke("interpret", binary, dump_file, "100", "206")
                    dumped = json.loads(dump_file.read_text(encoding="utf-8"))
                    original_cells = dict(zip(map(str, range(100, 107)),
                                              original))
                    result_cells = dict(zip(map(str, range(200, 207)),
                                            expected))
                    empty_cells = dict.fromkeys(map(str, range(107, 200)), 0)
                    expected_dump = (original_cells | empty_cells
                                     | result_cells)
                    self.assertEqual(dumped, expected_dump)
