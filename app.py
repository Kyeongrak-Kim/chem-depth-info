"""Development entry point for the chem-depth-info web app.

Run locally with:

    python app.py

Environment variables:
    HOST  interface to bind (default 0.0.0.0)
    PORT  port to bind (default 5000)
"""

from __future__ import annotations

import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
