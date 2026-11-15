"""
Абстрактен интерфейс за парсери на документи.

Модулът дефинира :class:`Parser` — базов интерфейс за всички парсери.
Всеки конкретен парсер знае как да прочете един файлов формат и да
върне сурови данни, без да се интересува от типа на документа.
"""

from abc import ABC, abstractmethod


class Parser(ABC):
    """Абстрактен интерфейс за парсер на файлове.

    Конкретните наследници (:class:`JsonParser`, :class:`CsvParser`)
    имплементират :meth:`parse` и връщат сурови данни, които после
    :mod:`documents.factory` превръща в :class:`documents.base.Document`.
    """

    @abstractmethod
    def parse(self, filename):
        """Прочита файл и връща суровите данни от него.

        Args:
            filename: Път до файла.

        Returns:
            За JSON — ``dict``; за CSV — ``list[dict]``.

        Raises:
            FileNotFoundError: Ако файлът не съществува.
            ValueError: Ако съдържанието не е валидно за формата.
        """
        pass
