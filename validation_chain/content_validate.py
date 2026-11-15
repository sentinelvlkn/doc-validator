"""
Handler, който изпълнява валидацията чрез Visitor шаблона.
"""

from visitors.validation_visitor import ValidationVisitor

from .handler import Handler


class ContentValidateHandler(Handler):
    """Стартира :class:`ValidationVisitor` върху ``ctx.document``."""

    def _process(self, ctx):
        """Изпълнява валидационния visitor и пренася грешките в контекста.

        Това е точката, в която **Visitor шаблонът** се среща с
        **Chain of Responsibility** — веригата решава *кога* да се
        валидира, а Visitor-ът решава *как*.

        Args:
            ctx: :class:`chain.handler.ValidationContext`.
        """
        if ctx.document is None:
            ctx.errors.append("Няма документ за валидация")
            return
        visitor = ValidationVisitor()
        errors = ctx.document.accept(visitor)
        ctx.errors.extend(errors)
