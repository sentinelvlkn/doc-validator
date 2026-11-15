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
import os
import tempfile

from werkzeug.exceptions import RequestEntityTooLarge

from flask import Flask, jsonify, render_template, request, redirect, send_from_directory

DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs_html",
)

from validation_chain import ValidationContext, build_chain
from visitors.summary_visitor import SummaryVisitor

app = Flask(__name__)

# Лимит за качване — 1 MB (защита срещу злонамерени файлове)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

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

def _respond(result, status=200):
    """Избира JSON или HTML отговор според ``Accept`` хедъра.

    Браузърите пращат ``Accept: text/html,...`` и получават HTML.
    API клиенти (curl, requests) пращат ``*/*`` и получават JSON.

    Args:
        result: Резултат от :func:`_validate_file`.
        status: HTTP статус код.

    Returns:
        flask.Response: JSON или HTML отговор.
    """
    if "text/html" in request.headers.get("Accept", ""):
        return render_template("index.html", result=result), status
    return jsonify(result), status

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

@app.route("/validate/upload", methods=["POST"])
def validate_upload():
    """Валидира качен файл чрез ``multipart/form-data``.

    Приема поле ``file``. Записва файла във временна директория със
    същото разширение, изпълнява веригата и изтрива временния файл.

    Returns:
        flask.Response: JSON (за API) или HTML (за браузър) с
        резултата.
    """
    if "file" not in request.files:
        return _respond(
            {"ok": False, "errors": ["Липсва поле 'file'"], "summary": None},
            400,
        )

    f = request.files["file"]
    if not f or f.filename == "":
        return _respond(
            {"ok": False, "errors": ["Не е избран файл"], "summary": None},
            400,
        )

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".json", ".csv"):
        return _respond(
            {
                "ok": False,
                "errors": [
                    f"Непозволено разширение: {ext or '(няма)'}. "
                    "Позволени: .json, .csv"
                ],
                "summary": None,
            },
            400,
        )

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    try:
        f.save(tmp_path)
        result = _validate_file(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return _respond(result)

@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(e):
    """Връща ясно съобщение при превишен размер на файла."""
    return jsonify({
        "ok": False,
        "errors": ["Файлът е твърде голям (макс. 1 MB)"],
        "summary": None,
    }), 413

@app.route("/health", methods=["GET"])
def health():
    """Прост health-check за Docker.

    Returns:
        flask.Response: ``{"status": "ok"}``.
    """
    return jsonify({"status": "ok"})

@app.route("/docs")
def docs_redirect():
    """Пренасочва /docs → /docs/ (за да работят относителните линкове)."""
    return redirect("/docs/")


@app.route("/docs/")
@app.route("/docs/<path:path>")
def serve_docs(path="index.html"):
    """Обслужва генерираната Sphinx HTML документация.

    Args:
        path: Относителен път в документацията.

    Returns:
        flask.Response: Файлът или 404, ако документацията не е
        генерирана.
    """
    if not os.path.isdir(DOCS_DIR):
        return jsonify({
            "error": "Документацията не е генерирана. "
                     "Изпълни `sphinx-build -b html source build/html` "
                     "в папка docs/.",
        }), 404
    return send_from_directory(DOCS_DIR, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
