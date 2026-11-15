"""
Базови класове за веригата отговорности (Chain of Responsibility).

Модулът дефинира:

- :class:`ValidationContext` — обектът, който пътува през веригата
  и се пълни от всеки handler (документ, формат, грешки);
- :class:`Handler` — абстрактен базов клас с общата логика за
  свързване и предаване на заявката към следващия handler.

Шаблонът Chain of Responsibility позволява заявката да бъде обработена
от поредица от независими проверки, без подателят да знае коя точно
проверка ще я обработи и кога веригата ще спре.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ValidationContext:
    """Контекст на една заявка за валидация.

    Обектът се създава веднъж в началото на веригата и се подава на
    всеки :class:`Handler`. Всеки handler може да го обогати (напр. да
    зададе ``document`` или ``file_format``) или да добави грешка.

    Attributes:
        filename: Пътят до файла, който се валидира (вход от
            потребителя).
        raw_data: Суровите данни, прочетени от парсера (``dict`` или
            ``list[dict]``). Попълва се от ``ParseHandler``.
        file_format: ``"json"`` или ``"csv"``. Попълва се от
            ``FormatDetectHandler``.
        document: Готовият :class:`documents.base.Document`. Попълва се
            от ``TypeCheckHandler``.
        errors: Списък със съобщения за грешки. Ако е непразен, веригата
            спира и резултатът се връща на потребителя.
    """

    filename: str
    raw_data: object = None
    file_format: str = None
    document: object = None
    errors: list = field(default_factory=list)

    @property
    def ok(self):
        """bool: ``True``, ако до момента няма натрупани грешки."""
        return not self.errors


class Handler(ABC):
    """Абстрактен базов клас за handler във веригата.

    Всеки конкретен handler наследява :class:`Handler` и имплементира
    :meth:`_process`. Логиката за предаване напред е обща и се намира
    в :meth:`handle`.
    """

    def __init__(self):
        self._next = None

    def set_next(self, handler):
        """Свързва следващия handler във веригата.

        Args:
            handler: Следващият :class:`Handler`.

        Returns:
            Handler: Подаденият ``handler`` — това позволява верижно
            свързване от вида ``h1.set_next(h2).set_next(h3)``.
        """
        self._next = handler
        return handler

    def handle(self, ctx):
        """Обработва контекста и го предава нататък, ако няма грешки.

        Извиква :meth:`_process` на текущия handler. Ако контекстът
        съдържа грешки — веригата спира. Иначе, ако има следващ
        handler, предава му контекста.

        Args:
            ctx: :class:`ValidationContext`.

        Returns:
            ValidationContext: Същият контекст, евентуално обогатен.
        """
        self._process(ctx)
        if not ctx.ok:
            return ctx
        if self._next is not None:
            return self._next.handle(ctx)
        return ctx

    @abstractmethod
    def _process(self, ctx):
        """Извършва конкретната проверка/операция на handler-а.

        Args:
            ctx: :class:`ValidationContext` — може да се чете и променя.
        """
        pass
