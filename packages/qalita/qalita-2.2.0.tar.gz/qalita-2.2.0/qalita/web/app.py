"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
from flask import Flask


def create_app(config_obj) -> Flask:
    """Application factory for the Qalita CLI UI."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "public"),
        static_url_path="/static",
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    )

    app.config["QALITA_CONFIG_OBJ"] = config_obj

    # Register blueprints
    from qalita.web.blueprints.main import bp as main_bp
    from qalita.web.blueprints.sources import bp as sources_bp
    from qalita.web.blueprints.studio import bp as studio_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(sources_bp, url_prefix="/sources")
    app.register_blueprint(studio_bp, url_prefix="/studio")

    return app


def run_dashboard_ui(config_obj, host: str = "localhost", port: int = 7070):
    app = create_app(config_obj)
    url = f"http://{host}:{port}"
    print(f"Qalita CLI UI is running. Open {url}")
    try:
        # Prefer a production-grade WSGI server to avoid Flask dev banner
        from waitress import serve  # type: ignore

        serve(app, host=host, port=port)
    except Exception:
        # Fallback to stdlib WSGI server (no banner)
        try:
            from wsgiref.simple_server import make_server

            with make_server(host, port, app) as httpd:
                httpd.serve_forever()
        except Exception:
            # Last resort fallback
            app.run(host=host, port=port, debug=False, use_reloader=False)


