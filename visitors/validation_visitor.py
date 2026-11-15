"""
Visitor за валидация на документ спрямо правилата в ``Field.meta``.

Този visitor прилага всички декларативни правила, дефинирани в
:mod:`documents.factory`, и връща списък със съобщения за грешки.
"""

import re
from datetime import date

from .visitor import Visitor


class ValidationVisitor(Visitor):
    """Обхожда документа и валидира всяко поле спрямо неговите правила.

    Attributes:
        errors: Списък с натрупаните съобщения за грешки. Попълва се
            по време на обхождането.
    """

    def __init__(self):
        self.errors = []

    def visit_document(self, doc):
        """Валидира всички полета и изпълнява кръстосаните проверки.

        Args:
            doc: :class:`documents.base.Document`.

        Returns:
            list: Списък със съобщения за грешки.
        """
        for field in doc.fields:
            field.accept(self)
        for check in doc.extra_checks:
            self.errors.extend(check(doc))
        return self.errors

    def visit_field(self, field):
        """Валидира едно поле спрямо неговите ``meta`` правила.

        Args:
            field: :class:`documents.base.Field`.
        """
        rules = field.meta
        value = field.value

        # 1. Задължително поле
        if rules.get("required") and self._is_empty(value):
            self.errors.append(f"{field.name}: задължително поле")
            return

        # 2. Незадължително и празно — няма какво да проверяваме
        if self._is_empty(value):
            return

        # 3. Преобразуване на типа (важно за CSV — там всичко е низ)
        try:
            converted = self._convert_type(value, rules.get("type"))
        except ValueError as e:
            self.errors.append(f"{field.name}: {e}")
            return

        # 4. Регулярен израз
        if "regex" in rules and not re.match(rules["regex"], str(converted)):
            self.errors.append(
                f"{field.name}: не отговаря на шаблона {rules['regex']}"
            )

        # 5. Числови граници
        if "min" in rules and converted < rules["min"]:
            self.errors.append(
                f"{field.name}: трябва да е >= {rules['min']}"
            )
        if "max" in rules and converted > rules["max"]:
            self.errors.append(
                f"{field.name}: трябва да е <= {rules['max']}"
            )

        # 6. Дължина на текст
        if "min_length" in rules and len(str(converted)) < rules["min_length"]:
            self.errors.append(
                f"{field.name}: твърде късо (мин. {rules['min_length']} знака)"
            )
        if "max_length" in rules and len(str(converted)) > rules["max_length"]:
            self.errors.append(
                f"{field.name}: твърде дълго (макс. {rules['max_length']} знака)"
            )

        # 7. Допустими стойности (enum)
        if "enum" in rules and converted not in rules["enum"]:
            self.errors.append(
                f"{field.name}: недопустима стойност {converted!r}, "
                f"очаква се едно от {rules['enum']}"
            )

        # 8. Връзка с текущата дата
        if "date_relation" in rules and isinstance(converted, date):
            today = date.today()
            if rules["date_relation"] == "not_future" and converted > today:
                self.errors.append(
                    f"{field.name}: датата не може да е в бъдещето"
                )
            elif rules["date_relation"] == "future" and converted <= today:
                self.errors.append(
                    f"{field.name}: датата трябва да е в бъдещето"
                )

    @staticmethod
    def _is_empty(value):
        """Проверява дали стойността е „празна“ в смисъла на ``required``.

        За разлика от ``not value``, тук ``0`` и ``False`` **не** се
        считат за празни (те са валидни стойности).

        Args:
            value: Произволна стойност.

        Returns:
            bool: ``True``, ако стойността е ``None``, ``""``, ``[]``
            или ``{}``.
        """
        return value is None or value == "" or value == [] or value == {}

    @staticmethod
    def _convert_type(value, type_name):
        """Преобразува стойността към очаквания тип.

        Args:
            value: Сурова стойност (обикновено низ от CSV).
            type_name: ``"int"``, ``"float"``, ``"str"``, ``"date"``
                или ``None``.

        Returns:
            Преобразуваната стойност.

        Raises:
            ValueError: Ако преобразуването е невъзможно.
        """
        if type_name is None or type_name == "str":
            return value
        if type_name == "int":
            try:
                return int(value)
            except (TypeError, ValueError):
                raise ValueError(f"очаква се цяло число, получено {value!r}")
        if type_name == "float":
            try:
                return float(value)
            except (TypeError, ValueError):
                raise ValueError(f"очаква се число, получено {value!r}")
        if type_name == "date":
            try:
                if isinstance(value, date):
                    return value
                return date.fromisoformat(str(value))
            except ValueError:
                raise ValueError(
                    f"очаква се дата във формат YYYY-MM-DD, получено {value!r}"
                )
        return value
