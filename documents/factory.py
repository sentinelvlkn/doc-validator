"""
Фабрика за създаване на :class:`documents.base.Document` обекти.

Модулът съдържа декларативни схеми с правила за валидация на трите
поддържани типа документи — фактура, доклад и заявка за материали —
и функции, които превръщат сурови данни (от JSON или CSV) в дърво
от :class:`documents.base.Field` обекти.

Схемите са речници, в които ключът е името на полето, а стойността е
речник с правила. Поддържани правила (интерпретират се от
``ValidationVisitor``):

- ``required`` (bool) — задължително поле;
- ``type`` (str) — ``"int"``, ``"float"``, ``"str"`` или ``"date"``;
- ``regex`` (str) — регулярен израз за стойността;
- ``min`` / ``max`` (number) — граници за числови стойности;
- ``min_length`` / ``max_length`` (int) — дължина за текстови стойности;
- ``enum`` (list) — списък с допустими стойности;
- ``date_relation`` (str) — ``"not_future"`` или ``"future"`` за дати.
"""

from .base import Document, Field


# ---------------------------------------------------------------------------
# Схема: ФАКТУРА (JSON)
# ---------------------------------------------------------------------------

INVOICE_FIELD_RULES = {
    "number": {"required": True, "type": "str",
               "regex": r"^INV-\d{4}-\d{3}$"},
    "date": {"required": True, "type": "date",
             "date_relation": "not_future"},
    "supplier.name": {"required": True, "type": "str"},
    "supplier.vat": {"required": True, "type": "str",
                     "regex": r"^BG\d{9}$"},
    "customer.name": {"required": True, "type": "str"},
    "customer.vat": {"required": True, "type": "str",
                     "regex": r"^BG\d{9}$"},
    "total": {"required": True, "type": "float", "min": 0},
}

INVOICE_ITEM_FIELD_RULES = {
    "description": {"required": True, "type": "str"},
    "quantity": {"required": True, "type": "int", "min": 1},
    "unit_price": {"required": True, "type": "float", "min": 0},
}


# ---------------------------------------------------------------------------
# Схема: ДОКЛАД (JSON)
# ---------------------------------------------------------------------------

REPORT_FIELD_RULES = {
    "title": {"required": True, "type": "str",
              "min_length": 3, "max_length": 200},
    "author": {"required": True, "type": "str"},
    "department": {"required": True, "type": "str",
                   "enum": ["Engineering", "Sales", "HR", "Finance"]},
    "date": {"required": True, "type": "date"},
    "pages": {"required": True, "type": "int", "min": 1, "max": 500},
    "content": {"required": False, "type": "str"},
}


# ---------------------------------------------------------------------------
# Схема: ЗАЯВКА ЗА МАТЕРИАЛИ (CSV)
# ---------------------------------------------------------------------------

MATERIAL_REQUEST_ROW_RULES = {
    "material": {"required": True, "type": "str"},
    "quantity": {"required": True, "type": "int", "min": 1},
    "unit": {"required": True, "type": "str",
             "enum": ["брой", "пакет", "кг", "литър"]},
    "urgency": {"required": True, "type": "str",
                "enum": ["low", "normal", "high"]},
    "deadline": {"required": True, "type": "date",
                 "date_relation": "future"},
}


# ---------------------------------------------------------------------------
# Помощни функции
# ---------------------------------------------------------------------------

def _get_nested(data, dotted_name):
    """Връща стойност от вложен речник по път с точки.

    Пример: ``_get_nested({"a": {"b": 1}}, "a.b")`` връща ``1``.

    Args:
        data: Речник (може да е вложен).
        dotted_name: Път с точки, напр. ``"supplier.vat"``.

    Returns:
        Стойността или ``None``, ако пътят не съществува.
    """
    current = data
    for key in dotted_name.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


# ---------------------------------------------------------------------------
# Кръстосани проверки (extra_checks)
# ---------------------------------------------------------------------------

def _invoice_extra_checks(doc):
    """Кръстосани проверки за фактура: непразен списък и коректен total.

    Args:
        doc: :class:`documents.base.Document` с попълнени полета.

    Returns:
        list: Списък от съобщения за грешки.
    """
    errors = []
    data = doc.as_dict()

    item_indices = sorted({
        int(name.split("[")[1].split("]")[0])
        for name in data
        if name.startswith("items[")
    })
    if not item_indices:
        errors.append("invoice: списъкът с артикули е празен")
        return errors

    expected_total = 0.0
    for i in item_indices:
        q = data.get(f"items[{i}].quantity")
        p = data.get(f"items[{i}].unit_price")
        if isinstance(q, (int, float)) and isinstance(p, (int, float)):
            expected_total += q * p

    total = data.get("total")
    if isinstance(total, (int, float)) and abs(total - expected_total) > 0.01:
        errors.append(
            f"invoice: total ({total}) не съвпада със сумата на "
            f"артикулите ({expected_total:.2f})"
        )
    return errors


def _material_request_extra_checks(doc):
    """Кръстосани проверки за заявка за материали: поне един ред.

    Args:
        doc: :class:`documents.base.Document`.

    Returns:
        list: Списък от съобщения за грешки.
    """
    if not any(f.name.startswith("row[") for f in doc.fields):
        return ["material_request: няма нито един ред"]
    return []


# ---------------------------------------------------------------------------
# Фабрични функции (по един builder за всеки тип)
# ---------------------------------------------------------------------------

def build_invoice(data):
    """Построява :class:`Document` за фактура от суров речник.

    Args:
        data: Речник, получен от JSON-а на фактурата.

    Returns:
        Document: Документ с попълнени полета и ``extra_checks``.
    """
    fields = []

    for name, rule in INVOICE_FIELD_RULES.items():
        fields.append(Field(name, _get_nested(data, name), rule))

    items = data.get("items")
    if isinstance(items, list):
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            for sub, rule in INVOICE_ITEM_FIELD_RULES.items():
                full_name = f"items[{i}].{sub}"
                fields.append(Field(full_name, item.get(sub), rule))

    return Document(
        doc_type="invoice",
        fields=fields,
        file_format="json",
        extra_checks=[_invoice_extra_checks],
    )


def build_report(data):
    """Построява :class:`Document` за доклад от суров речник.

    Args:
        data: Речник, получен от JSON-а на доклада.

    Returns:
        Document: Документ с попълнени полета.
    """
    fields = [
        Field(name, _get_nested(data, name), rule)
        for name, rule in REPORT_FIELD_RULES.items()
    ]
    return Document(
        doc_type="report",
        fields=fields,
        file_format="json",
    )


def build_material_request(rows):
    """Построява :class:`Document` за заявка за материали от редове.

    Args:
        rows: Списък от речници — един речник на ред от CSV файла.

    Returns:
        Document: Документ с по едно поле за всяка клетка.
    """
    fields = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        for sub, rule in MATERIAL_REQUEST_ROW_RULES.items():
            full_name = f"row[{i}].{sub}"
            fields.append(Field(full_name, row.get(sub), rule))

    return Document(
        doc_type="material_request",
        fields=fields,
        file_format="csv",
        extra_checks=[_material_request_extra_checks],
    )
