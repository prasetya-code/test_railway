from flask import Blueprint, current_app, request

from config.log_system import app_logger, security_event

from app.extensions.flask_limit import fl_limiter

import time, hashlib

debug_bp = Blueprint('debug', __name__)


# =========================
# APPS DEBUG
# =========================

# # for PWA
# @debug_bp.route('/service-worker.js')
# def service_worker():
#     return current_app.send_static_file('sw.js')


# =========================
# CONTAINER ROUTES
# =========================

# # check container health
# @debug_bp.route("/health")
# @fl_limiter.exempt
# def health():
#     # ✅ Operational log (normal activity)
#     app_logger.info("Health check endpoint hit")

#     return "Container Health Check"


# =========================
# POLICY ROUTES
# =========================

# @debug_bp.route('/csp-report', methods=['POST'])
# def csp_report():
#     """
#     JSON-only CSP report endpoint.
#     """

#     # =========================
#     # VALIDASI CONTENT TYPE
#     # =========================
#     if request.content_type not in (
#         "application/csp-report",
#         "application/json"
#     ):
#         return '', 204

#     report = request.get_json(silent=True)
#     if not report:
#         return '', 204

#     csp = report.get("csp-report") or report

#     blocked = csp.get("blocked-uri", "")
#     violated = csp.get("violated-directive", "")

#     # =========================
#     # FILTER NOISE (EXTENSION)
#     # =========================
#     if blocked.startswith(("chrome-extension://", "moz-extension://")):
#         return '', 204

#     # =========================
#     # DEDUP (60 detik)
#     # =========================
#     key = hashlib.sha256(f"{blocked}{violated}".encode()).hexdigest()
#     now = int(time.time())

#     cache = current_app.config.setdefault("_CSP_CACHE", {})

#     if key in cache and now - cache[key] < 60:
#         return '', 204

#     cache[key] = now

#     # =========================
#     # 🚨 SECURITY LOG (utama)
#     # =========================
#     security_event.warning(
#         "CSP violation detected",
#         extra={
#             "threat_type": "csp_violation",
#             "severity": "low",
#             "blocked": False,
#             "rule_matched": violated
#         }
#     )

#     # =========================
#     # 🧾 OPTIONAL DEBUG (APP LOG)
#     # =========================
#     app_logger.debug(
#         f"CSP detail: blocked={blocked}, violated={violated}"
#     )

#     return '', 204