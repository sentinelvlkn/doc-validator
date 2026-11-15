"""
Visitor, който връща кратко резюме за документа.

Демонстрира, че Visitor шаблонът може да прави и операции, различни от
валидация, без да се променя структурата на документа.
"""

from .visitor import Visitor


class SummaryVisitor(Visitor):
    """Събира обобщена информация за документа.

    Attributes:
        doc_type: Тип на документа, попълва се при посещението.
        field_count: Брой посетени полета.
        empty_count: Брой полета с празна стойност.
    """

    def __init__(self):
        self.doc_type = None
        self.field_count = 0
        self.empty_count = 0

    def visit_document(self, doc):
        """Обхожда всички полета и връща резюме.

        Args:
            doc: :class:`documents.base.Document`.

        Returns:
            dict: Резюме с ключове ``type``, ``fields``,
            ``empty_fields`` и ``format``.
        """
        self.doc_type = doc.doc_type
        for field in doc.fields:
            field.accept(self)
        return {
            "type": self.doc_type,
            "fields": self.field_count,
            "empty_fields": self.empty_count,
            "format": doc.file_format,
        }

    def visit_field(self, field):
        """Брои полетата и празните стойности.

        Args:
            field: :class:`documents.base.Field`.
        """
        self.field_count += 1
        if field.value in (None, "", [], {}):
            self.empty_count += 1
