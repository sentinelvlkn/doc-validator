"""
Конфигурация на Sphinx за проекта Doc Validator.

Генерира документация в HTML, DOCX и PDF от:

- docstrings в кода (чрез ``autodoc`` и ``napoleon``);
- ръчно написани ``.rst`` файлове;
- PlantUML диаграми (чрез ``sphinxcontrib-plantuml``).
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


# -- Информация за проекта ------------------------------------------------

project = "Doc Validator"
author = "Тодор Николов"
copyright = "2026, Тодор Николов"
release = "1.0.0"
language = "bg"


# -- Разширения -----------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",            # API от docstrings
    "sphinx.ext.napoleon",           # поддръжка на Google/NumPy стил
    "sphinx.ext.viewcode",           # линк към изходния код
    "sphinx.ext.todo",               # TODO бележки
    "sphinxcontrib.plantuml",        # PlantUML диаграми
    "docxbuilder",                   # .docx изход
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False


# -- PlantUML -------------------------------------------------------------

plantuml = "plantuml"
plantuml_output_format = "png"

# -- Autodoc --------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_mock_imports = []   

# -- HTML ----------------------------------------------------------------

html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "light_css_variables": {
        "font-stack": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "font-stack--monospace": "'JetBrains Mono', 'Fira Code', monospace",
    },
    "dark_css_variables": {
        "color-brand-primary": "#66b2ff",
        "color-brand-content": "#79c0ff",
    },
}
html_static_path = ["_static"]

html_css_files = ["custom.css"]

pygments_style = "friendly"
pygments_dark_style = "monokai"


# -- LaTeX (за PDF) ------------------------------------------------------

latex_documents = [
    ("index", "DocValidator.tex", "Doc Validator",
     "Тодор Николов", "manual"),
]
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "preamble": r"""
        \usepackage[utf8]{inputenc}
        \usepackage[T2A]{fontenc}
        \usepackage[bulgarian]{babel}
    """,
}


# -- DOCX (docxbuilder) --------------------------------------------------

docxbuilder_heading_style_map = {
    "title": "Title",
    "rubric": "Heading 1",
    "section": "Heading 1",
    "subsection": "Heading 2",
    "subsubsection": "Heading 3",
}

docxbuilder_use_admonition = True
docxbuilder_table_style = "Table Grid"


# -- Други ---------------------------------------------------------------

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
todo_include_todos = True


def setup(app):
    """Регистрира handler за PlantUML node в DocxBuilder."""

    def docx_visit_plantuml(self, node):
        """Визуализира PlantUML диаграма и я вмъква като изображение в DOCX."""

        def get_filepath(self, node):
            from sphinxcontrib import plantuml
            _, filepath = plantuml.render_plantuml(self, node, "png")
            return filepath

        alt = node.get("alt", (node["uml"], None))
        self.visit_image_node(node, alt, get_filepath)

    import docxbuilder

    translator = docxbuilder.DocxBuilder.default_translator_class
    setattr(translator, "visit_plantuml", docx_visit_plantuml)
