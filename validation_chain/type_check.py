"""
Handler, който определя типа на документа и го построява чрез фабриката.
"""

from documents.factory import (
    build_invoice,
    build_material_request,
    build_report,
)

from .handler import Handler


class TypeCheckHandler(Handler):
    """Определя типа на документа и създава :class:`Document` чрез фабриката."""

    def _process(self, ctx):
        """Построява ``ctx.document`` според ``ctx.file_format`` и данните.

        За JSON типът се чете от полето ``type`` във файла. За CSV
        единственият поддържан тип е ``material_request``.

        Args:
            ctx: :class:`chain.handler.ValidationContext`.
        """
        if ctx.file_format == "json":
            if not isinstance(ctx.raw_data, dict):
                ctx.errors.append("JSON файлът трябва да съдържа обект")
                return
            doc_type = ctx.raw_data.get("type")
            if doc_type == "invoice":
                ctx.document = build_invoice(ctx.raw_data)
            elif doc_type == "report":
                ctx.document = build_report(ctx.raw_data)
            else:
                ctx.errors.append(f"Непознат тип документ: {doc_type!r}")
        elif ctx.file_format == "csv":
            ctx.document = build_material_request(ctx.raw_data)
        else:
            ctx.errors.append(f"Неподдържан формат: {ctx.file_format}")
