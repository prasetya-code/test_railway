from flask import request
from urllib.parse import urlparse
from pathlib import Path

from config.logging.log_parser import app_logger

# ============================================================
# 🔧 FILE HANDLER CONFIG & UTILS (Pathlib + Scalable + Logging)
# ============================================================


# -----------------------------
# Allowed extensions per type
# -----------------------------
ALLOWED_EXTENSIONS = {
    "images": {".jpg", ".jpeg", ".png", ".svg", ".webp", ".gif"},
    "files": {".pdf"},
    "animate": {".json"},
}

# -----------------------------
# Trusted referers per type
# -----------------------------
TRUSTED_REFERERS = {
    "images": {"prasetyacode.com", "localhost", "127.0.0.1"},
    "files": {"prasetyacode.com", "localhost", "127.0.0.1"},
    "animate": {"prasetyacode.com", "localhost", "127.0.0.1"},
}


# ============================================================
# 🔒 Validasi referer
# ============================================================
def is_trusted_referer(file_type: str) -> bool:
    """
    Cek apakah request berasal dari trusted referer untuk tipe file tertentu.
    - file_type: 'images', 'audio', 'files', dsb.
    """
    referer = request.headers.get("Referer")
    trusted_hosts = TRUSTED_REFERERS.get(file_type, set())

    # ✅ Jika tidak ada referer, cek Accept header untuk images
    if not referer:
        accept = request.headers.get("Accept", "")
        if file_type == "images" and accept.startswith("image/"):
            return True

        app_logger.warning(f"Referer kosong untuk file_type={file_type}, ditolak")
        return False

    hostname = urlparse(referer).hostname
    app_logger.debug(f"[Referer Check] File type={file_type}, Host={hostname}")

    trusted = any(
        hostname == trusted_host or (hostname and hostname.endswith("." + trusted_host))
        for trusted_host in trusted_hosts
    )

    if not trusted:
        app_logger.warning(
            f"Referer tidak trusted: {hostname} untuk file_type={file_type}"
        )
    return trusted


# ============================================================
# 🔒 Validasi ekstensi
# ============================================================
def is_allowed_file(filename: str, file_type: str) -> bool:
    """
    Cek apakah file termasuk ekstensi yang diizinkan.
    """
    allowed = ALLOWED_EXTENSIONS.get(file_type, set())
    ext = Path(filename).suffix.lower()

    if ext not in allowed:
        app_logger.warning(
            f"File extension tidak diperbolehkan: {filename} untuk tipe {file_type}"
        )

    return ext in allowed


# ============================================================
# 🔒 Validasi path aman
# ============================================================
def is_safe_path(filename: str, base_dir: str = ".") -> bool:
    """
    Pastikan file path aman dan tidak menembus root directory.
    - filename: path file yang akan dicek
    - base_dir: root directory untuk validasi
    """
    base_path = Path(base_dir).resolve()
    file_path = (base_path / filename).resolve()

    safe = base_path in file_path.parents or file_path == base_path
    if not safe:
        app_logger.warning(f"Path tidak aman: {file_path} (base: {base_path})")

    return safe
