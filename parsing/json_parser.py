"""
Парсер за JSON файлове.
"""

import json

from .parser import Parser


class JsonParser(Parser):
    """Чете JSON файл и връща съдържанието като речник.

    Използва се за типовете ``invoice`` и ``report``.
    """

    def parse(self, filename):
        """Прочита JSON файл.

        Args:
            filename: Път до ``.json`` файла.

        Returns:
            dict: Съдържанието на файла.

        Raises:
            FileNotFoundError: Ако файлът не съществува.
            ValueError: Ако файлът не е валиден JSON.
        """
        try:
            with open(filename, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Невалиден JSON във {filename}: {e}") from e
