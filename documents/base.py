"""
Базови класове за представяне на документи като дървовидна структура.

Модулът дефинира абстрактния интерфейс :class:`DocumentElement`,
който позволява на Visitor шаблона да обхожда елементите на документа,
както и конкретните класове :class:`Field` и :class:`Document`.
"""

from abc import ABC, abstractmethod


class DocumentElement(ABC):
    """Абстрактен елемент от дървото на документа.

    Всеки елемент поддържа Visitor шаблона чрез метода :meth:`accept`.
    Това позволява добавяне на нови операции (валидация, резюме,
    експорт) без промяна на класовете на елементите — класическата
    мотивация за прилагане на шаблона Visitor.
    """

    @abstractmethod
    def accept(self, visitor):
        """Приема Visitor и му делегира обработката на този елемент.

        Args:
            visitor: Обект, наследяващ :class:`visitors.visitor.Visitor`.

        Returns:
            Резултатът от съответния ``visit_*`` метод на visitor-а.
        """
        pass


class Field(DocumentElement):
    """Листов елемент на документа — едно поле със стойност и правила.

    Args:
        name: Име на полето (напр. ``"number"`` или ``"supplier.vat"``).
        value: Стойността на полето.
        meta: Речник с правила за валидация. Поддържани ключове:

            - ``required`` (bool) — задължително поле;
            - ``regex`` (str) — регулярен израз, на който стойността
              трябва да отговаря;
            - ``min`` / ``max`` (number) — долна / горна граница;
            - ``enum`` (list) — списък с допустими стойности;
            - ``type`` (str) — ``"int"``, ``"float"``, ``"str"``
              или ``"date"``.
    """

    def __init__(self, name, value, meta=None):
        self.name = name
        self.value = value
        self.meta = meta or {}

    def accept(self, visitor):
        """Делегира обработката на ``visitor.visit_field(self)``.

        Args:
            visitor: Обект, наследяващ :class:`visitors.visitor.Visitor`.

        Returns:
            Резултатът от ``visitor.visit_field``.
        """
        return visitor.visit_field(self)

    def __repr__(self):
        return f"Field({self.name!r}, {self.value!r})"


class Document(DocumentElement):
    """Коренов елемент — цял документ, съдържащ списък от полета.

    Args:
        doc_type: Тип на документа (``"invoice"``, ``"report"`` или
            ``"material_request"``).
        fields: Списък от :class:`Field` обекти.
        file_format: Формат на изходния файл (``"json"`` или ``"csv"``).
    """

    def __init__(self, doc_type, fields, file_format):
        self.doc_type = doc_type
        self.fields = fields
        self.file_format = file_format

    def accept(self, visitor):
        """Делегира обработката на ``visitor.visit_document(self)``.

        Args:
            visitor: Обект, наследяващ :class:`visitors.visitor.Visitor`.

        Returns:
            Резултатът от ``visitor.visit_document``.
        """
        return visitor.visit_document(self)

    def __repr__(self):
        return f"Document({self.doc_type!r}, {len(self.fields)} fields)"
