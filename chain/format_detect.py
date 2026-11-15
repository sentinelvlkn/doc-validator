"""
Handler, който определя формата на файла по разширението.
"""

import os

from .handler import Handler


class FormatDetectHandler(Handler):
    """Определя ``file_format`` (``"json"`` или ``"csv"``) от разширението."""

    def _process(self, ctx):
        """Записва формата в контекста.

        Args:
            ctx: :class:`chain.handler.ValidationContext`.
        """
        ext = os.path.splitext(ctx.filename)[1].lower()
        ctx.file_format = ext.lstrip(".")
