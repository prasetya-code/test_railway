# flask-talisman memang hanya fokus ke security response headers saja

from pathlib import Path
import os
import json
import tempfile
import traceback

from datetime import datetime

from flask_talisman import Talisman

# =========================
# TALISMAN INSTANCE
# =========================
fl_talisman = Talisman()

# =========================
# CONFIG DIRECTORY
# =========================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

TALISMAN_PATH = PROJECT_ROOT / "tmp" / "flask_talisman"


def ensure_cache_dir():
    try:
        TALISMAN_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(f"[CACHE] Directory ready: {TALISMAN_PATH}")

    except Exception as e:
        print(f"[CACHE ERROR] Failed to create cache directory: {e}")

        traceback.print_exc()


def write_json_file(filename, data):
    """
    Safe JSON writer
    """

    try:
        filepath = TALISMAN_PATH / filename

        # Membuat file temporary terlebih dahulu, jika proses gagal atau crash, file asli tidak ikut rusak.
        with tempfile.NamedTemporaryFile(
            # File dibuka dalam mode write
            mode="w",
            # Gunakan UTF-8 agar karakter unicode aman
            encoding="utf-8",
            # Jangan otomatis dihapus saat file ditutup
            delete=False,
            # Simpan file temporary di folder yang sama
            dir=TALISMAN_PATH,
            # Tambahkan ekstensi sementara
            suffix=".tmp",
        ) as file:
            # Konversi object Python menjadi JSON
            # lalu tulis ke file temporary
            json.dump(
                # Data Python yang akan ditulis
                data,
                # Objek file tujuan
                file,
                # JSON lebih rapi dan mudah dibaca
                indent=4,
                # Jangan ubah unicode menjadi escape sequence
                ensure_ascii=False,
                # Jika ada object yang tidak bisa
                # di-serialize JSON (datetime, Path, dll)
                # maka otomatis diubah menjadi string
                default=str,
                # Urutkan key JSON secara alfabetis
                # agar hasil selalu konsisten
                sort_keys=True,
            )

            # Paksa buffer Python ditulis ke OS
            file.flush()

            # Paksa OS benar-benar menyimpan data ke disk
            os.fsync(file.fileno())

            # Simpan nama file temporary
            temp_name = file.name

        # Setelah file temporary selesai ditulis, ganti file tujuan secara atomik.
        # Jika sebelumnya ada maka akan langsung diganti oleh file temporary yang sudah lengkap.
        os.replace(
            temp_name,
            filepath,
        )

        # Beri tanda bahwa proses berhasil
        return True

    except Exception:
        # Tampilkan traceback lengkap ke console/log
        traceback.print_exc()

        # Beri tanda bahwa proses gagal
        return False


def export_talisman_config(app, csp):
    """
    Export talisman configuration
    """
    try:
        data = {
            "generated_at": datetime.utcnow().isoformat(),
            "force_https": app.config.get("FORCE_HTTPS"),
            "frame_options": app.config.get("FRAME_OPTIONS"),
            "referrer_policy": app.config.get("REFERRER_POLICY"),
            "strict_transport_security": app.config.get("STRICT_TRANSPORT_SECURITY"),
            "strict_transport_security_preload": app.config.get(
                "STRICT_TRANSPORT_SECURITY_PRELOAD"
            ),
            "strict_transport_security_max_age": app.config.get(
                "STRICT_TRANSPORT_SECURITY_MAX_AGE"
            ),
            "session_cookie_secure": app.config.get("SESSION_COOKIE_SECURE"),
            "session_cookie_httponly": app.config.get("SESSION_COOKIE_HTTPONLY"),
            "session_cookie_samesite": app.config.get("SESSION_COOKIE_SAMESITE"),
            "content_security_policy": csp,
        }

        write_json_file(
            "talisman_config.json",
            data,
        )

    except Exception:
        app.logger.exception("[TALISMAN JSON] Failed to export configuration")

    # # =========================
    # # CONFIG (STATIC ONLY)
    # # =========================
    # class TalismanConfig:
    #     FORCE_HTTPS = (
    #         os.getenv(
    #             "FORCE_HTTPS",
    #             "false",
    #         ).lower()
    #         == "true"
    #     )

    #     STRICT_TRANSPORT_SECURITY = True
    #     STRICT_TRANSPORT_SECURITY_PRELOAD = True
    #     STRICT_TRANSPORT_SECURITY_MAX_AGE = 31536000

    #     FRAME_OPTIONS = "DENY"

    #     CONTENT_TYPE_NOSNIFF = True

    #     REFERRER_POLICY = (
    #         "strict-origin-when-cross-origin"
    #     )

    #     CONTENT_SECURITY_POLICY = {
    #         "default-src": ["'self'"],
    #         "script-src": ["'self'"],
    #         "style-src": ["'self'"],
    #         "img-src": [
    #             "'self'",
    #             "data:",
    #         ],
    #         "font-src": ["'self'"],
    #         "connect-src": ["'self'"],
    #         "frame-ancestors": ["'none'"],
    #         "base-uri": ["'self'"],
    #         "object-src": ["'none'"],
    #         "form-action": ["'self'"],
    #     }

    #     SESSION_COOKIE_SECURE = True
    #     SESSION_COOKIE_HTTPONLY = True
    #     SESSION_COOKIE_SAMESITE = "Lax"

    #     FORCE_CONTENT_SECURITY_POLICY = True

    # # =========================
    # # CSP CUSTOM OVERRIDE
    # # =========================
    # def get_custom_csp(app):
    #     try:
    #         csp_mode = os.getenv(
    #             "CSP_MODE",
    #             "strict",
    #         ).lower()

    #         if csp_mode == "strict":
    #             return (
    #                 TalismanConfig
    #                 .CONTENT_SECURITY_POLICY
    #             )

    #         elif csp_mode == "dev":
    #             return {
    #                 "default-src": ["'self'"],
    #                 "script-src": [
    #                     "'self'",
    #                     "'unsafe-inline'",
    #                 ],
    #                 "style-src": [
    #                     "'self'",
    #                     "'unsafe-inline'",
    #                 ],
    #                 "img-src": [
    #                     "'self'",
    #                     "data:",
    #                     "*",
    #                 ],
    #                 "connect-src": [
    #                     "'self'",
    #                     "*",
    #                 ],
    #                 "object-src": [
    #                     "'none'"
    #                 ],
    #                 "form-action": [
    #                     "'self'"
    #                 ],
    #             }

    #         elif csp_mode == "app":
    #             return app.config.get(
    #                 "CUSTOM_CSP",
    #                 TalismanConfig
    #                 .CONTENT_SECURITY_POLICY,
    #             )

    #         return (
    #             TalismanConfig
    #             .CONTENT_SECURITY_POLICY
    #         )

    #     except Exception:
    #         app.logger.exception(
    #             "[TALISMAN CSP ERROR] "
    #             "Failed to load custom CSP"
    #         )

    #         return (
    #             TalismanConfig
    #             .CONTENT_SECURITY_POLICY
    #         )

    # def register_header_audit(app):
    #     """
    #     Runtime security header auditing
    #     """

    #     @app.after_request
    #     def audit_security_headers(response):
    #         try:
    #             monitored_headers = {
    #                 "Content-Security-Policy",
    #                 "Strict-Transport-Security",
    #                 "X-Frame-Options",
    #                 "X-Content-Type-Options",
    #                 "Referrer-Policy",
    #                 "Permissions-Policy",
    #                 "Cross-Origin-Opener-Policy",
    #                 "Cross-Origin-Resource-Policy",
    #             }

    #             data = {
    #                 "generated_at":
    #                     datetime.utcnow().isoformat(),
    #                 "headers": {},
    #             }

    #             for header in monitored_headers:
    #                 value = response.headers.get(
    #                     header
    #                 )

    #                 if value:
    #                     data["headers"][
    #                         header
    #                     ] = value

    #             write_json_file(
    #                 "runtime_headers.json",
    #                 data,
    #             )

    #         except Exception:
    #             app.logger.exception(
    #                 "[TALISMAN AUDIT] "
    #                 "Failed to audit headers"
    #             )

    #         return response

    # def register_extra_security_headers(app):
    #     """
    #     Modern browser security headers
    #     """

    #     @app.after_request
    #     def add_security_headers(response):

    #         response.headers[
    #             "Permissions-Policy"
    #         ] = (
    #             "camera=(), "
    #             "microphone=(), "
    #             "geolocation=(), "
    #             "payment=(), "
    #             "usb=(), "
    #             "fullscreen=(self)"
    #         )

    #         response.headers[
    #             "Cross-Origin-Opener-Policy"
    #         ] = "same-origin"

    #         response.headers[
    #             "Cross-Origin-Resource-Policy"
    #         ] = "same-origin"

    #         return response

    # # =========================
    # # INIT TALISMAN
    # # =========================
    # def init_talisman(app):
    # try:
    #     ensure_cache_dir()

    #     app.config.from_object(TalismanConfig)

    #     app.logger.info("[TALISMAN] Loading configuration...")

    #     enable_security = (
    #         os.getenv(
    #             "ENABLE_TALISMAN",
    #             "true",
    #         ).lower()
    #         == "true"
    #     )

    #     if not enable_security:
    #         app.logger.warning("[TALISMAN] Disabled via ENV (ENABLE_TALISMAN=false)")

    #         return

    #     force_https = app.config.get(
    #         "FORCE_HTTPS",
    #         False,
    #     )

    #     csp = get_custom_csp(app)

    #     app.logger.info(
    #         "[TALISMAN] FORCE_HTTPS=%s",
    #         force_https,
    #     )

    #     fl_talisman.init_app(
    #         app,
    #         force_https=force_https,
    #         content_security_policy=csp,
    #         frame_options=app.config.get("FRAME_OPTIONS"),
    #         strict_transport_security=True,
    #         strict_transport_security_max_age=app.config.get(
    #             "STRICT_TRANSPORT_SECURITY_MAX_AGE"
    #         ),
    #         strict_transport_security_preload=app.config.get(
    #             "STRICT_TRANSPORT_SECURITY_PRELOAD"
    #         ),
    #         session_cookie_secure=app.config.get("SESSION_COOKIE_SECURE"),
    #         session_cookie_http_only=app.config.get("SESSION_COOKIE_HTTPONLY"),
    #         session_cookie_samesite=app.config.get("SESSION_COOKIE_SAMESITE"),
    #     )

    #     register_extra_security_headers(app)

    #     register_header_audit(app)

    #     export_talisman_config(
    #         app,
    #         csp,
    #     )

    #     app.logger.info("[TALISMAN] Initialized successfully")

    # except Exception:
    #     app.logger.exception("[TALISMAN ERROR] Failed to initialize")

    #     # =========================
    #     # FALLBACK SAFE MODE
    #     # =========================
    #     try:
    #         app.logger.warning("[TALISMAN] Falling back to minimal security mode")

    #         fl_talisman.init_app(
    #             app,
    #             force_https=False,
    #             content_security_policy={"default-src": ["'self'"]},
    #         )

    #         register_extra_security_headers(app)

    #         register_header_audit(app)

    #         export_talisman_config(
    #             app,
    #             {"default-src": ["'self'"]},
    #         )

    #         app.logger.info("[TALISMAN] Fallback initialized successfully")

    #     except Exception:
    #         app.logger.critical(
    #             "[TALISMAN CRITICAL] Fallback initialization failed",
    #             exc_info=True,
    #         )

    #         raise
