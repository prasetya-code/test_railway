import traceback

from .app_routes import main_bp
from .monitor_routes import monitor_bp
from .file_routes import file_bp
from .data_routes import data_bp

BLUEPRINTS = [
    main_bp,
    monitor_bp,
    file_bp,
    data_bp,
]


def register_routes(app):
    try:
        for bp in BLUEPRINTS:
            app.register_blueprint(bp)

    except Exception as e:
        print("\nROUTE gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()
