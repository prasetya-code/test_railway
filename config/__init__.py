import traceback
import time

from flask import g


def register_config(app):

    try:
        from .logging.log_parser import (
            app_logger,
            access_logger,
            security_event,
        )

        # expose ke app context (opsional tapi bagus)
        app.app_logger = app_logger
        app.access_logger = access_logger

        # SECURITY tidak perlu expose kalau hanya pakai helper
        app.security_event = security_event

        # =========================================
        # BEFORE REQUEST (tracking response time)
        # =========================================

        @app.before_request
        def log_before_request():
            g.start_time = time.time()

        # =========================================
        # AFTER REQUEST (ACCESS LOG AUTOMATIC)
        # =========================================

        @app.after_request
        def log_after_request(response):

            response_time = round(
                (time.time() - g.start_time) * 1000,
                2,
            )

            # cukup 1 line — tanpa extra
            access_logger.info(
                "HTTP_REQUEST",
                extra={
                    "status_code": response.status_code,
                    "bytes_sent": response.calculate_content_length(),
                    "response_time": response_time,
                },
            )

            return response

        # =========================================
        # APP STARTUP LOG
        # =========================================

        app_logger.info("APPLICATION_INITIALIZED")

    except Exception as e:
        print("\nLOGGER gagal diinisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()
