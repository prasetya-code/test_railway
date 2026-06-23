import traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect
from sqlalchemy.exc import (
    OperationalError,
    ProgrammingError,
    DatabaseError,
    SQLAlchemyError,
)

alch_db = SQLAlchemy()

# Flag internal: mencegah init_database() dijalankan lebih dari sekali
_DB_INITIALIZED = False


# =============================================================
# SECTION 1: DATABASE CONNECTION
# =============================================================

DB_DRIVER   = "postgresql+psycopg"
DB_USER     = "user"
DB_PASSWORD = "password"
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "app_db"

DATABASE_URI = (
    f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# =============================================================
# SECTION 2: SQLALCHEMY BEHAVIOR CONFIG
# =============================================================

# Nonaktifkan event tracking — hemat memori, wajib False di production
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Tampilkan query SQL di console — aktifkan hanya saat development
SQLALCHEMY_ECHO = False

# Rekam query untuk profiling/debugging (gunakan bersama get_debug_queries())
SQLALCHEMY_RECORD_QUERIES = True

# Batas waktu eksekusi query sebelum dianggap "lambat" (dalam detik)
SQLALCHEMY_SLOW_DB_QUERY_TIME_WARNING = 0.5

# Commit otomatis setelah setiap request — set False agar kontrol manual
SQLALCHEMY_COMMIT_ON_TEARDOWN = False


# =============================================================
# SECTION 3: CONNECTION POOL CONFIG
# =============================================================

# Jumlah koneksi permanen yang selalu terbuka ke database
POOL_SIZE = 10

# Koneksi tambahan saat pool_size habis
# Total koneksi maksimal = pool_size + max_overflow
MAX_OVERFLOW = 20

# Waktu tunggu (detik) mendapatkan koneksi dari pool sebelum raise error
POOL_TIMEOUT = 30

# Waktu hidup koneksi (detik) sebelum di-recycle — cegah koneksi "basi"
# 1800 = 30 menit; sesuaikan dengan wait_timeout di PostgreSQL
POOL_RECYCLE = 1800

# Kirim "SELECT 1" sebelum memakai koneksi — deteksi koneksi mati lebih awal
POOL_PRE_PING = True

# Gunakan SQLAlchemy 2.x style API (wajib True untuk psycopg3 / modern stack)
ENGINE_FUTURE = True


# =============================================================
# SECTION 4: EXECUTION & QUERY OPTIONS
# =============================================================

# Opsi tambahan per-eksekusi (read-only transaction, deferrable, dsb.)
EXECUTION_OPTIONS = {
    "execution_options": {
        "postgresql_readonly": False,      # Set True untuk read-only transactions
        "postgresql_deferrable": False,    # Untuk serializable isolation level
    }
}

# Opsi koneksi dikirim langsung ke driver psycopg
CONNECT_ARGS = {
    "connect_timeout": 10,                    # Timeout koneksi awal ke server (detik)
    "options": "-c statement_timeout=30000",  # Batas waktu query: 30 detik (ms)
}


# =============================================================
# SECTION 5: SESSION CONFIG
# =============================================================

SESSION_OPTIONS = {
    "expire_on_commit": True,   # Objek expired setelah commit (default SQLAlchemy)
    "autoflush": True,          # Flush otomatis sebelum query
    "autocommit": False,        # Selalu False — commit harus eksplisit
}


# =============================================================
# SECTION 6: AUTO CREATE TABLE
# Nonaktifkan jika menggunakan Flask-Migrate (Alembic)
# =============================================================

USE_AUTO_CREATE_TABLES = False  # Ganti True hanya untuk dev/testing tanpa Migrate


# =============================================================
# BUILDER FUNCTIONS
# =============================================================

def _build_engine_options() -> dict:
    """
    Menggabungkan semua konfigurasi engine SQLAlchemy menjadi satu dict.
    Diteruskan ke SQLALCHEMY_ENGINE_OPTIONS.
    """
    return {
        "pool_size":     POOL_SIZE,
        "max_overflow":  MAX_OVERFLOW,
        "pool_timeout":  POOL_TIMEOUT,
        "pool_recycle":  POOL_RECYCLE,
        "pool_pre_ping": POOL_PRE_PING,
        "future":        ENGINE_FUTURE,
        "connect_args":  CONNECT_ARGS,
        **EXECUTION_OPTIONS,
    }


def _build_sqlalchemy_config() -> dict:
    """
    Menggabungkan semua parameter SQLAlchemy ke dalam satu dict config Flask.
    """
    return {
        "SQLALCHEMY_DATABASE_URI":        DATABASE_URI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": SQLALCHEMY_TRACK_MODIFICATIONS,
        "SQLALCHEMY_ECHO":                SQLALCHEMY_ECHO,
        "SQLALCHEMY_RECORD_QUERIES":      SQLALCHEMY_RECORD_QUERIES,
        "SQLALCHEMY_ENGINE_OPTIONS":      _build_engine_options(),
    }


# =============================================================
# VALIDATION FUNCTIONS
# =============================================================

def _validate_config() -> None:
    """
    Validasi variabel konfigurasi sebelum diterapkan ke app.
    Raise ValueError jika ada nilai yang tidak valid.
    """
    errors = []

    if not DATABASE_URI or "://" not in DATABASE_URI:
        errors.append(f"DATABASE_URI tidak valid: '{DATABASE_URI}'")

    if not DB_USER or not DB_USER.strip():
        errors.append("DB_USER tidak boleh kosong.")

    if not DB_PASSWORD or not DB_PASSWORD.strip():
        errors.append("DB_PASSWORD tidak boleh kosong.")

    if not DB_HOST or not DB_HOST.strip():
        errors.append("DB_HOST tidak boleh kosong.")

    if not isinstance(DB_PORT, int) or not (1 <= DB_PORT <= 65535):
        errors.append(f"DB_PORT harus integer antara 1–65535, dapat: '{DB_PORT}'")

    if not DB_NAME or not DB_NAME.strip():
        errors.append("DB_NAME tidak boleh kosong.")

    if not isinstance(POOL_SIZE, int) or POOL_SIZE < 1:
        errors.append(f"POOL_SIZE harus integer >= 1, dapat: '{POOL_SIZE}'")

    if not isinstance(MAX_OVERFLOW, int) or MAX_OVERFLOW < 0:
        errors.append(f"MAX_OVERFLOW harus integer >= 0, dapat: '{MAX_OVERFLOW}'")

    if not isinstance(POOL_TIMEOUT, (int, float)) or POOL_TIMEOUT <= 0:
        errors.append(f"POOL_TIMEOUT harus angka > 0, dapat: '{POOL_TIMEOUT}'")

    if not isinstance(POOL_RECYCLE, (int, float)) or POOL_RECYCLE <= 0:
        errors.append(f"POOL_RECYCLE harus angka > 0, dapat: '{POOL_RECYCLE}'")

    if errors:
        msg = "Validasi konfigurasi database gagal:\n  - " + "\n  - ".join(errors)
        print(f"[DB][ERROR] {msg}")
        raise ValueError(msg)

    print("[DB][OK] Validasi konfigurasi database berhasil.")


def _validate_db_not_initialized() -> None:
    """
    Cegah init_database() dipanggil lebih dari sekali dalam satu proses.
    Raise RuntimeError jika sudah pernah diinisialisasi.
    """
    if _DB_INITIALIZED:
        msg = (
            "init_database() sudah dipanggil sebelumnya. "
            "Panggilan duplikat diabaikan untuk mencegah re-init."
        )
        print(f"[DB][WARNING] {msg}")
        raise RuntimeError(msg)


# =============================================================
# CORE FUNCTIONS
# =============================================================

def _apply_config(app) -> None:
    """
    Menerapkan semua config SQLAlchemy ke Flask app.config.
    Raise RuntimeError jika config gagal diterapkan.
    """
    try:
        config = _build_sqlalchemy_config()
        for key, value in config.items():
            app.config[key] = value
        print("[DB][OK] Konfigurasi SQLAlchemy berhasil diterapkan ke app.")
    except Exception:
        print("[DB][ERROR] Gagal menerapkan konfigurasi SQLAlchemy.")
        print(traceback.format_exc())
        raise RuntimeError(
            "Gagal menerapkan konfigurasi database ke Flask app.\n"
            + traceback.format_exc()
        )


def _init_extension(app) -> None:
    """
    Mendaftarkan SQLAlchemy extension ke Flask app.
    Raise RuntimeError jika ekstensi gagal diinisialisasi.
    """
    try:
        alch_db.init_app(app)
        print("[DB][OK] Ekstensi SQLAlchemy berhasil diinisialisasi.")
    except Exception:
        print("[DB][ERROR] Gagal menginisialisasi ekstensi SQLAlchemy.")
        print(traceback.format_exc())
        raise RuntimeError(
            "Gagal menginisialisasi ekstensi SQLAlchemy.\n"
            + traceback.format_exc()
        )


def _verify_connection(app) -> None:
    """
    Verifikasi koneksi aktual ke PostgreSQL dengan menjalankan 'SELECT 1'.
    Raise OperationalError atau DatabaseError jika koneksi gagal.
    """
    try:
        with app.app_context():
            with alch_db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        print(f"[DB][OK] Koneksi ke PostgreSQL berhasil: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except OperationalError:
        print(
            f"[DB][ERROR] Tidak dapat terhubung ke database '{DB_NAME}' "
            f"di {DB_HOST}:{DB_PORT}. Periksa kredensial dan status server."
        )
        print(traceback.format_exc())
        raise
    except DatabaseError:
        print("[DB][ERROR] Terjadi error database saat verifikasi koneksi.")
        print(traceback.format_exc())
        raise


def _get_existing_tables(app) -> set[str]:
    """
    Mengambil daftar nama tabel yang sudah ada di database.

    Returns:
        Set nama tabel yang sudah ada di schema 'public'.
    """
    with app.app_context():
        inspector = inspect(alch_db.engine)
        existing = set(inspector.get_table_names(schema="public"))
    return existing


def _create_tables(app) -> None:
    """
    Membuat tabel yang belum ada di database secara aman (idempotent).

    - db.create_all() secara internal menggunakan IF NOT EXISTS —
      tabel yang sudah ada tidak akan di-drop atau direkrasi ulang.
    - Diff sebelum/sesudah digunakan untuk melaporkan tabel mana
      yang baru dibuat vs yang sudah ada dan dilewati.
    - Tidak melakukan apa-apa jika USE_AUTO_CREATE_TABLES = False.

    PERINGATAN: Jangan digunakan bersamaan dengan Flask-Migrate (Alembic).
    """
    if not USE_AUTO_CREATE_TABLES:
        print(
            "[DB][INFO] AUTO CREATE TABLE dinonaktifkan (USE_AUTO_CREATE_TABLES=False). "
            "Gunakan Flask-Migrate untuk manajemen skema."
        )
        return

    try:
        # Snapshot tabel SEBELUM create_all
        existing_before = _get_existing_tables(app)

        with app.app_context():
            # create_all pakai IF NOT EXISTS — aman, tidak overwrite tabel lama
            alch_db.create_all()

        # Snapshot tabel SETELAH create_all untuk diff
        existing_after = _get_existing_tables(app)

        newly_created  = existing_after - existing_before
        already_existed = existing_after & existing_before

        if newly_created:
            print(
                f"[DB][OK] Tabel baru berhasil dibuat ({len(newly_created)}): "
                + ", ".join(sorted(newly_created))
            )
        else:
            print("[DB][INFO] Tidak ada tabel baru yang dibuat.")

        if already_existed:
            print(
                f"[DB][INFO] Tabel sudah ada, dilewati ({len(already_existed)}): "
                + ", ".join(sorted(already_existed))
            )

    except ProgrammingError:
        print(
            "[DB][ERROR] ProgrammingError saat membuat tabel. "
            "Periksa definisi model atau hak akses user database."
        )
        print(traceback.format_exc())
        raise
    except OperationalError:
        print(
            "[DB][ERROR] OperationalError saat membuat tabel. "
            "Koneksi ke database mungkin terputus."
        )
        print(traceback.format_exc())
        raise
    except SQLAlchemyError:
        print("[DB][ERROR] SQLAlchemyError tidak terduga saat create_all().")
        print(traceback.format_exc())
        raise


# =============================================================
# ENTRYPOINT UTAMA
# =============================================================

def init_database(app):
    """
    Inisialisasi lengkap database ke Flask app dengan validasi dan error handling.

    Urutan eksekusi:
        1. Cegah duplikat inisialisasi (guard flag)
        2. Validasi semua variabel konfigurasi
        3. Terapkan config ke app.config
        4. Daftarkan ekstensi SQLAlchemy
        5. Verifikasi koneksi aktual ke PostgreSQL
        6. (Opsional) Buat tabel baru yang belum ada

    Args:
        app: Flask application instance

    Returns:
        app: Flask application instance (sudah terkonfigurasi)

    Raises:
        RuntimeError     : Jika config gagal diterapkan.
        ValueError       : Jika ada variabel konfigurasi yang tidak valid.
        OperationalError : Jika koneksi ke PostgreSQL gagal.
        SQLAlchemyError  : Jika create_all() mengalami error tak terduga.
    """
    global _DB_INITIALIZED

    print("=" * 60)
    print("[DB] Memulai inisialisasi database...")
    print("=" * 60)

    try:
        # Step 1 — Guard duplikat
        _validate_db_not_initialized()

        # Step 2 — Validasi config
        _validate_config()

        # Step 3 — Terapkan config ke Flask app
        _apply_config(app)

        # Step 4 — Init ekstensi db
        _init_extension(app)

        # Step 5 — Verifikasi koneksi nyata ke server
        _verify_connection(app)

        # Step 6 — Buat tabel (idempotent, skip jika sudah ada)
        _create_tables(app)

        # Tandai sudah berhasil diinisialisasi
        _DB_INITIALIZED = True

        print("=" * 60)
        print("[DB][OK] Database berhasil diinisialisasi.")
        print("=" * 60)

    except RuntimeError as e:
        # Duplikat init — tidak perlu crash app, cukup return
        print(f"[DB][WARNING] {e}")
        return app

    except ValueError as e:
        # Config tidak valid — fatal, harus diperbaiki sebelum app jalan
        print(f"[DB][CRITICAL] Konfigurasi tidak valid: {e}")
        print(traceback.format_exc())
        raise

    except OperationalError as e:
        # Koneksi gagal — fatal
        print(f"[DB][CRITICAL] Tidak dapat terhubung ke database: {e}")
        print(traceback.format_exc())
        raise

    except ProgrammingError as e:
        # Skema/model error — fatal
        print(f"[DB][CRITICAL] Error definisi tabel atau hak akses: {e}")
        print(traceback.format_exc())
        raise

    except SQLAlchemyError as e:
        # Tangkap semua SQLAlchemy error yang tidak ter-handle di atas
        print(f"[DB][CRITICAL] SQLAlchemyError tidak terduga: {e}")
        print(traceback.format_exc())
        raise

    except Exception as e:
        # Fallback untuk error di luar SQLAlchemy (bug, TypeError, dsb.)
        print(f"[DB][CRITICAL] Error tidak terduga saat init database: {e}")
        print(traceback.format_exc())
        raise

    return app