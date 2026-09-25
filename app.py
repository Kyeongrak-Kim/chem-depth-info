"""Development entry point for the chem-depth-info web app.

Run locally with:

    python app.py

Environment variables:
    HOST         interface to bind (default 0.0.0.0)
    PORT         port to bind (default 5000)
    FLASK_DEBUG  1/true to enable the debugger and reloader (default 1)
"""

from __future__ import annotations

import os

from app import create_app

app = create_app()


def _env_flag(name: str, default: str = "1") -> bool:
    return os.environ.get(name, default).strip().lower() not in {"0", "false", "no", "off"}


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = _env_flag("FLASK_DEBUG", "1")
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
