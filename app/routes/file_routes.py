from pathlib import Path

from flask import Blueprint, send_from_directory, abort, current_app

from app.extensions.flask_limit import fl_limiter

from app.utils.protected_manager import (
    is_trusted_referer,
    is_allowed_file,
    is_safe_path,
)

from app.utils.well_known_manager import ensure_well_known

from config.log_system import app_logger, security_event

file_bp = Blueprint("file", __name__)


# ============================================================
# PRIVATE FILE SERVING (Cek validasi asset di dir private)
# ============================================================
def serve_private_file(file_type: str, filename: str, base_subdir: str):
    base_dir = Path(current_app.root_path) / "private" / base_subdir

    file_path = base_dir / filename

    # ========================================================
    # PATH VALIDATION
    # ========================================================
    if not is_safe_path(file_path, base_dir):
        security_event("PATH_TRAVERSAL")
        abort(403)

    # ========================================================
    # EXTENSION VALIDATION
    # ========================================================
    if not is_allowed_file(filename, file_type):
        security_event("INVALID_FILE", rule_matched=f"type:{file_type}")
        abort(403)

    # ========================================================
    # REFERER VALIDATION
    # ========================================================
    if not is_trusted_referer(file_type):
        security_event("INVALID_REFERER")
        abort(403)

    # ========================================================
    # SUCCESS
    # ========================================================
    app_logger.info(f"Serving private file → type={file_type}, file={filename}")

    return send_from_directory(base_dir, filename)


# ============================================================
# ROUTES
# ============================================================
@file_bp.route("/images/<path:filename>")
@fl_limiter.exempt
def protected_image(filename):
    return serve_private_file("images", filename, "images")


@file_bp.route("/files/<path:filename>")
@fl_limiter.exempt
def protected_files(filename):
    return serve_private_file("files", filename, "files")


@file_bp.route("/animate/<path:filename>")
@fl_limiter.exempt
def protected_animate(filename):
    return serve_private_file("animate", filename, "animate")


# ============================================================
# .well-known (lokasi standar agar sistem lain bisa menemukan konfigurasi atau metadata domain Anda tanpa perlu tahu URL khusus.)
# ============================================================
@file_bp.route("/.well-known/<path:filename>")
@fl_limiter.exempt
def serve_well_known(filename):

    static_dir = Path(current_app.static_folder)
    well_known_dir = static_dir / ".well-known"

    try:
        # ====================================================
        # ENSURE FILES EXIST
        # ====================================================
        ensure_well_known()

        file_path = (well_known_dir / filename).resolve()

        # ====================================================
        # PATH VALIDATION
        # ====================================================
        if not str(file_path).startswith(str(well_known_dir.resolve())):
            security_event("PATH_TRAVERSAL")
            abort(403)

        # ====================================================
        # FILE NOT FOUND
        # ====================================================
        if not file_path.exists():
            app_logger.info(f".well-known file not found → {filename}")
            return "", 204

        # ====================================================
        # SUCCESS
        # ====================================================
        app_logger.info(f"Serving .well-known file → {filename}")

        return send_from_directory(well_known_dir, filename)

    except Exception as exc:
        security_event("FILE_SERVING_ERROR", filename=filename, error=str(exc))

        app_logger.exception(f"Error serving .well-known file: {filename}")

        abort(500)
