"""
Handler, който прочита файла чрез подходящия парсер.
"""

from parsing.csv_parser import CsvParser
from parsing.json_parser import JsonParser

from .handler import Handler


class ParseHandler(Handler):
    """Прочита файла и записва суровите данни в ``ctx.raw_data``."""

    def _process(self, ctx):
        """Избира парсер според ``ctx.file_format`` и парсва файла.

        Args:
            ctx: :class:`chain.handler.ValidationContext`.
        """
        try:
            if ctx.file_format == "json":
                ctx.raw_data = JsonParser().parse(ctx.filename)
            elif ctx.file_format == "csv":
                ctx.raw_data = CsvParser().parse(ctx.filename)
            else:
                ctx.errors.append(f"Неподдържан формат: {ctx.file_format}")
        except (OSError, ValueError) as e:
            ctx.errors.append(f"Грешка при четене: {e}")
