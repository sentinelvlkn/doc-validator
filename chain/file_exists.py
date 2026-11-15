"""
Handler, който проверява дали файлът съществува и е с позволено разширение.
"""

import os

from .handler import Handler

ALLOWED_EXTENSIONS = (".json", ".csv")


class FileExistsHandler(Handler):
    """Проверява, че файлът съществува и е с разширение ``.json`` или ``.csv``."""

    def _process(self, ctx):
        """Добавя грешка, ако файлът липсва или разширението е непозволено.

        Args:
            ctx: :class:`chain.handler.ValidationContext`.
        """
        if not os.path.isfile(ctx.filename):
            ctx.errors.append(f"Файлът не съществува: {ctx.filename}")
            return
        if not ctx.filename.lower().endswith(ALLOWED_EXTENSIONS):
            ctx.errors.append(
                f"Позволени разширения: {', '.join(ALLOWED_EXTENSIONS)}"
            )
