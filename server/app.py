"""
Flask приложение за валидация на документи.

Предоставя два маршрута:

- ``GET /`` — HTML форма за въвеждане на име на файл;
- ``POST /validate`` — JSON API, който приема ``{"filename": "..."}``
  и връща резултата от валидацията.

Цялата логика за валидация е изнесена във веригата отговорности
(:mod:`chain`), така че сървърът е само тънък слой между HTTP и
домейн логиката.
"""

from flask import Flask, jsonify, render_template, request

from validation_chain import ValidationContext, build_chain
from visitors.summary_visitor import SummaryVisitor

app = Flask(__name__)


def _validate_file(filename):
    """Изпълнява веригата за валидация върху един файл.

    Args:
        filename: Път до файла.

    Returns:
        dict: Резултат с ключове ``ok``, ``errors``, ``summary``.
    """
    ctx = build_chain().handle(ValidationContext(filename=filename))
    summary = None
    if ctx.document is not None:
        summary = ctx.document.accept(SummaryVisitor())
    return {
        "ok": ctx.ok,
        "errors": ctx.errors,
        "summary": summary,
    }


@app.route("/", methods=["GET"])
def index():
    """Показва HTML формата за валидация."""
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate():
    """Валидира файл, подаден като JSON или като HTML форма.

    Приема ``filename`` като:

    - JSON: ``{"filename": "samples/invoice_ok.json"}``;
    - form-data: поле ``filename``.

    Returns:
        flask.Response: JSON с ``ok``, ``errors`` и ``summary``
        (при JSON заявка) или HTML страница с резултата (при
        form заявка).
    """
    if request.is_json:
        data = request.get_json(silent=True) or {}
        filename = data.get("filename")
        if not filename:
            return jsonify({"ok": False,
                            "errors": ["Липсва поле 'filename'"],
                            "summary": None}), 400
        return jsonify(_validate_file(filename))

    filename = request.form.get("filename", "")
    if not filename:
        return render_template("index.html",
                               error="Въведи име на файл"), 400
    result = _validate_file(filename)
    return render_template("index.html", filename=filename,
                           result=result)


@app.route("/health", methods=["GET"])
def health():
    """Прост health-check за Docker.

    Returns:
        flask.Response: ``{"status": "ok"}``.
    """
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
