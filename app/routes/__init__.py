import traceback


def register_routes(app):
    try:
        from .app_routes import main_bp
        from .monitor_routes import monitor_bp
        from .file_routes import file_bp
        from .data_routes import data_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(monitor_bp)
        app.register_blueprint(file_bp)
        app.register_blueprint(data_bp)

    except Exception as e:
        print("\nROUTE gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()
