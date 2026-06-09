import traceback


def register_config(app):
    try:
        from .logging.log_parser import (
            app_logger,
            access_logger,
            security_logger,
        )

        app.app_logger = app_logger
        app.access_logger = access_logger
        app.security_logger = security_logger

        app_logger.info("APP logger initialized")
        access_logger.info("ACCESS logger initialized")
        security_logger.info("SECURITY logger initialized")

    except Exception as e:
        print("\nLOGGER gagal diinisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()
