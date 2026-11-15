"""
Парсер за CSV файлове.
"""

import csv

from .parser import Parser


class CsvParser(Parser):
    """Чете CSV файл и връща списък от речници (един на ред).

    Използва се за типа ``material_request``.
    """

    def parse(self, filename):
        """Прочита CSV файл.

        Args:
            filename: Път до ``.csv`` файла.

        Returns:
            list[dict]: Всеки ред е речник с ключове от заглавния ред.

        Raises:
            FileNotFoundError: Ако файлът не съществува.
        """
        with open(filename, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
