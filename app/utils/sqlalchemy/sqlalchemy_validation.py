import traceback
from .sqlalchemy_config import *

# Flag global untuk mencegah init double
_DB_INITIALIZED = False


def validate_config():
    print("[DEBUG] Memulai validasi konfigurasi...")

    try:
        errors = []

        print("[DEBUG] Mengecek DATABASE_URI...")
        if not DATABASE_URI or "://" not in DATABASE_URI:
            errors.append("DATABASE_URI tidak valid")

        print("[DEBUG] Mengecek DB_USER...")
        if not DB_USER.strip():
            errors.append("DB_USER kosong")

        print("[DEBUG] Mengecek DB_PASSWORD...")
        if not DB_PASSWORD.strip():
            errors.append("DB_PASSWORD kosong")

        print("[DEBUG] Mengecek DB_HOST...")
        if not DB_HOST.strip():
            errors.append("DB_HOST kosong")

        print("[DEBUG] Mengecek DB_PORT...")
        if not isinstance(DB_PORT, int) or not (1 <= DB_PORT <= 65535):
            errors.append("DB_PORT invalid")

        print("[DEBUG] Mengecek DB_NAME...")
        if not DB_NAME.strip():
            errors.append("DB_NAME kosong")

        print("[DEBUG] Mengecek POOL_SIZE...")
        if POOL_SIZE < 1:
            errors.append("POOL_SIZE invalid")

        print("[DEBUG] Mengecek MAX_OVERFLOW...")
        if MAX_OVERFLOW < 0:
            errors.append("MAX_OVERFLOW invalid")

        print("[DEBUG] Mengecek POOL_TIMEOUT...")
        if POOL_TIMEOUT <= 0:
            errors.append("POOL_TIMEOUT invalid")

        print("[DEBUG] Mengecek POOL_RECYCLE...")
        if POOL_RECYCLE <= 0:
            errors.append("POOL_RECYCLE invalid")

        if errors:
            msg = "Config error:\n - " + "\n - ".join(errors)
            print("[ERROR] Validasi gagal!")
            print(msg)
            raise ValueError(msg)

        print("[DEBUG] Validasi konfigurasi berhasil.")

    except Exception as e:
        print("[EXCEPTION] Terjadi error saat validasi konfigurasi!")
        traceback.print_exc()
        raise  # tetap lempar ulang agar tidak disembunyikan


def validate_not_initialized():
    global _DB_INITIALIZED

    print("[DEBUG] Mengecek status inisialisasi DB...")

    try:
        if _DB_INITIALIZED:
            raise RuntimeError("Database sudah diinisialisasi sebelumnya")

        print("[DEBUG] Database belum diinisialisasi.")

    except Exception:
        print("[EXCEPTION] Error pada validate_not_initialized!")
        traceback.print_exc()
        raise