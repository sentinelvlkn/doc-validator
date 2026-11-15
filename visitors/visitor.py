"""
Абстрактен интерфейс за Visitor шаблона.

Всеки конкретен visitor наследява :class:`Visitor` и имплементира
двата метода — :meth:`visit_document` и :meth:`visit_field`. По този
начин нови операции над документа се добавят като нов клас, без да се
променя кодът на :class:`documents.base.Document` или
:class:`documents.base.Field`.
"""

from abc import ABC, abstractmethod


class Visitor(ABC):
    """Абстрактен visitor за елементите на документ."""

    @abstractmethod
    def visit_document(self, doc):
        """Посещава кореновия елемент на документа.

        Args:
            doc: :class:`documents.base.Document`.

        Returns:
            Резултат, специфичен за конкретния visitor.
        """
        pass

    @abstractmethod
    def visit_field(self, field):
        """Посещава едно поле на документа.

        Args:
            field: :class:`documents.base.Field`.

        Returns:
            Резултат, специфичен за конкретния visitor (обикновено
            ``None`` — visitor-ът натрупва резултата в себе си).
        """
        pass
