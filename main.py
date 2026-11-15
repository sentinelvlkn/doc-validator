"""
CLI входна точка за валидация на документ.

Употреба::

    python main.py samples/invoice_ok.json
    python main.py samples/invoice_ok.json samples/report_bad.json
"""

import sys

from validation_chain import ValidationContext, build_chain


def validate(filename):
    """Валидира един файл и отпечатва резултата.

    Args:
        filename: Път до файла.

    Returns:
        bool: ``True`` при валиден документ, ``False`` иначе.
    """
    ctx = build_chain().handle(ValidationContext(filename=filename))
    print(f"\n=== {filename} ===")
    if ctx.ok:
        doc = ctx.document
        print(f"  ✓ Валиден ({doc.doc_type}, {len(doc.fields)} полета)")
        return True
    for err in ctx.errors:
        print(f"  ✗ {err}")
    return False


def main(argv):
    """Точка на влизане за CLI.

    Args:
        argv: Списък с аргументи (обикновено ``sys.argv[1:]``).

    Returns:
        int: Код за изход — ``0`` при успех, ``1`` при поне един
        невалиден файл или при липса на аргументи.
    """
    if not argv:
        print("Употреба: python main.py <файл> [<файл> ...]")
        return 1
    results = [validate(fn) for fn in argv]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
