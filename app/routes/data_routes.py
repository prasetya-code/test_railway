from flask import Blueprint, send_from_directory, current_app

from app.extensions.flask_limit import fl_limiter

from config.log_system import app_logger


data_bp = Blueprint("data", __name__)


# =================
# ROBOTS
# =================
@data_bp.route("/robots.txt")
@fl_limiter.exempt
def robots():
    app_logger.info("robots.txt requested")

    return send_from_directory(
        current_app.static_folder, "robots.txt", mimetype="text/plain"
    )
