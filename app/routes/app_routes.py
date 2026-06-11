from flask import Blueprint, render_template

from app.extensions.flask_cache import fl_cache
from app.extensions.flask_limit import fl_limiter

from config.log_system import (
    app_logger,
    security_event,
)

main_bp = Blueprint("main", __name__)


# =========================
# APP ROUTES
# =========================


@main_bp.route("/", methods=["GET"])
@fl_limiter.limit("5 per minute")
@fl_cache.cached(
    timeout=60, response_filter=lambda r: getattr(r, "status_code", 200) == 200
)
def index():

    # APP LOG (manual event aplikasi)
    app_logger.info("HOME_PAGE_ACCESSED")

    return render_template("app/index.html")


# =========================
# ERROR HANDLER
# =========================


@main_bp.app_errorhandler(429)
def ratelimit_handler(e):

    # SECURITY LOG (rate limit = security event)
    security_event("RATE_LIMIT_EXCEEDED")

    return render_template("handler/429.html"), 429


@main_bp.app_errorhandler(405)
def method_not_allowed_handler(e):

    # 405 bukan security critical,
    # cukup masuk ACCESS logger otomatis (tidak perlu log manual)

    app_logger.warning("METHOD_NOT_ALLOWED")

    return render_template("handler/405.html"), 405
