"""
Пакет за веригата отговорности (Chain of Responsibility).

Предоставя функция :func:`build_chain`, която сглобява всички handler-и
в правилния ред.
"""

from .content_validate import ContentValidateHandler
from .file_exists import FileExistsHandler
from .format_detect import FormatDetectHandler
from .handler import Handler, ValidationContext
from .parse_handler import ParseHandler
from .type_check import TypeCheckHandler


def build_chain():
    """Сглобява веригата от всички handler-и в правилния ред.

    Returns:
        Handler: Първият handler от веригата.
    """
    h1 = FileExistsHandler()
    h2 = FormatDetectHandler()
    h3 = ParseHandler()
    h4 = TypeCheckHandler()
    h5 = ContentValidateHandler()
    h1.set_next(h2).set_next(h3).set_next(h4).set_next(h5)
    return h1
