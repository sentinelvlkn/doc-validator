"""
WSGI входна точка за gunicorn в Docker контейнера.

Пример::

    gunicorn --bind 0.0.0.0:5000 wsgi:app
"""

from server.app import app

if __name__ == "__main__":
    app.run()
