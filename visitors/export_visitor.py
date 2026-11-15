"""
Visitor, който експортира документа обратно в речник.

Демонстрира, че един и същ документ може да бъде обект на различни
операции (валидация, резюме, експорт) чрез различни visitor-и, без
промяна в класовете на елементите.
"""

from .visitor import Visitor


class ExportVisitor(Visitor):
    """Събира полетата на документа в речник ``{име: стойност}``."""

    def __init__(self):
        self.data = {}

    def visit_document(self, doc):
        """Обхожда документа и връща експортираните данни.

        Args:
            doc: :class:`documents.base.Document`.

        Returns:
            dict: Речник с всички полета на документа.
        """
        self.data = {"type": doc.doc_type, "format": doc.file_format}
        for field in doc.fields:
            field.accept(self)
        return self.data

    def visit_field(self, field):
        """Добавя полето към резултатния речник.

        Args:
            field: :class:`documents.base.Field`.
        """
        self.data[field.name] = field.value
