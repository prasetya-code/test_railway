import traceback
from flask_migrate import Migrate, init, migrate, upgrade, downgrade, current, history
from ...temp_code.temp_database import fl_db


# =============================================================
# FLASK-MIGRATE INSTANCE
# =============================================================

flask_migrate = Migrate()


# =============================================================
# SECTION 1: MIGRATE CONFIG
# =============================================================

# Direktori tempat menyimpan file migrasi Alembic
MIGRATE_DIRECTORY = "migrations"

# Render as batch — wajib True untuk SQLite, opsional untuk PostgreSQL
# Set True jika sering ALTER TABLE di PostgreSQL via Alembic
MIGRATE_RENDER_AS_BATCH = False

# Bandingkan tipe kolom saat autogenerate (misal VARCHAR(50) vs TEXT)
MIGRATE_COMPARE_TYPE = True

# Bandingkan nilai default kolom saat autogenerate
MIGRATE_COMPARE_SERVER_DEFAULT = False

# Include schema selain 'public' (isi jika pakai multi-schema)
# Contoh: MIGRATE_INCLUDE_SCHEMAS = ["public", "audit"]
MIGRATE_INCLUDE_SCHEMAS: list[str] = []

# Include object selain Table (misal: sequence, index, trigger)
# Lihat: https://alembic.sqlalchemy.org/en/latest/api/runtime.html
MIGRATE_INCLUDE_OBJECT = None  # callable atau None


# =============================================================
# SECTION 2: ALEMBIC CONTEXT OPTIONS
# Diteruskan langsung ke Alembic env.py via configure_args
# =============================================================

ALEMBIC_CONTEXT_OPTS = {
    "compare_type":           MIGRATE_COMPARE_TYPE,
    "compare_server_default": MIGRATE_COMPARE_SERVER_DEFAULT,
    "render_as_batch":        MIGRATE_RENDER_AS_BATCH,
    **({"include_schemas": MIGRATE_INCLUDE_SCHEMAS} if MIGRATE_INCLUDE_SCHEMAS else {}),
    **({"include_object": MIGRATE_INCLUDE_OBJECT} if MIGRATE_INCLUDE_OBJECT else {}),
}


# =============================================================
# BUILDER FUNCTION
# =============================================================

def _build_migrate_config() -> dict:
    """
    Membangun dict konfigurasi untuk Migrate().
    """
    return {
        "directory":      MIGRATE_DIRECTORY,
        "render_as_batch": MIGRATE_RENDER_AS_BATCH,
        "configure_args": ALEMBIC_CONTEXT_OPTS,
    }


# =============================================================
# CORE FUNCTIONS
# =============================================================

def _validate_migrate_config() -> None:
    """
    Validasi konfigurasi Flask-Migrate sebelum diinisialisasi.
    Raise ValueError jika ada nilai yang tidak valid.
    """
    errors = []

    if not MIGRATE_DIRECTORY or not MIGRATE_DIRECTORY.strip():
        errors.append("MIGRATE_DIRECTORY tidak boleh kosong.")

    if not isinstance(MIGRATE_COMPARE_TYPE, bool):
        errors.append(f"MIGRATE_COMPARE_TYPE harus bool, dapat: '{MIGRATE_COMPARE_TYPE}'")

    if not isinstance(MIGRATE_COMPARE_SERVER_DEFAULT, bool):
        errors.append(
            f"MIGRATE_COMPARE_SERVER_DEFAULT harus bool, "
            f"dapat: '{MIGRATE_COMPARE_SERVER_DEFAULT}'"
        )

    if not isinstance(MIGRATE_RENDER_AS_BATCH, bool):
        errors.append(
            f"MIGRATE_RENDER_AS_BATCH harus bool, dapat: '{MIGRATE_RENDER_AS_BATCH}'"
        )

    if not isinstance(MIGRATE_INCLUDE_SCHEMAS, list):
        errors.append(
            f"MIGRATE_INCLUDE_SCHEMAS harus list, dapat: '{type(MIGRATE_INCLUDE_SCHEMAS)}'"
        )

    if errors:
        msg = "Validasi konfigurasi Flask-Migrate gagal:\n  - " + "\n  - ".join(errors)
        print(f"[MIGRATE][ERROR] {msg}")
        raise ValueError(msg)

    print("[MIGRATE][OK] Validasi konfigurasi Flask-Migrate berhasil.")


def _init_migrate_extension(app) -> None:
    """
    Mendaftarkan Flask-Migrate ke app dan db.
    Raise RuntimeError jika gagal.
    """
    try:
        config = _build_migrate_config()
        flask_migrate.init_app(
            app,
            fl_db,
            directory=config["directory"],
            render_as_batch=config["render_as_batch"],
            configure_args=config["configure_args"],
        )
        print(
            f"[MIGRATE][OK] Flask-Migrate berhasil diinisialisasi. "
            f"Direktori migrasi: '{MIGRATE_DIRECTORY}'"
        )
    except Exception:
        print("[MIGRATE][ERROR] Gagal menginisialisasi Flask-Migrate.")
        print(traceback.format_exc())
        raise RuntimeError(
            "Gagal menginisialisasi Flask-Migrate.\n" + traceback.format_exc()
        )


# =============================================================
# MIGRATION HELPER FUNCTIONS
# Wrapper tipis di atas perintah Flask-Migrate CLI —
# berguna untuk dipakai secara programatik (test, CI/CD, script)
# =============================================================

def run_init(directory: str = MIGRATE_DIRECTORY) -> None:
    """
    Inisialisasi folder migrasi Alembic (flask db init).
    Hanya dijalankan SEKALI saat pertama setup project.

    Raise:
        RuntimeError jika folder sudah ada atau init gagal.
    """
    try:
        print(f"[MIGRATE][INFO] Menjalankan 'flask db init' ke '{directory}'...")
        init(directory=directory)
        print(f"[MIGRATE][OK] Folder migrasi '{directory}' berhasil dibuat.")
    except Exception:
        print(f"[MIGRATE][ERROR] Gagal menginisialisasi folder migrasi '{directory}'.")
        print(traceback.format_exc())
        raise RuntimeError(
            f"Gagal menginisialisasi folder migrasi '{directory}'.\n"
            + traceback.format_exc()
        )


def run_migrate(message: str = "auto migration") -> None:
    """
    Generate file migrasi baru berdasarkan perubahan model (flask db migrate).

    Args:
        message: Pesan/label untuk file migrasi yang dibuat.

    Raise:
        RuntimeError jika autogenerate gagal.
    """
    try:
        print(f"[MIGRATE][INFO] Membuat file migrasi baru: '{message}'...")
        migrate(message=message)
        print(f"[MIGRATE][OK] File migrasi '{message}' berhasil dibuat.")
    except Exception:
        print(f"[MIGRATE][ERROR] Gagal membuat file migrasi '{message}'.")
        print(traceback.format_exc())
        raise RuntimeError(
            f"Gagal membuat file migrasi '{message}'.\n" + traceback.format_exc()
        )


def run_upgrade(revision: str = "head") -> None:
    """
    Terapkan migrasi ke database hingga revision tertentu (flask db upgrade).

    Args:
        revision: Target revision Alembic. Default 'head' = versi terbaru.

    Raise:
        RuntimeError jika upgrade gagal.
    """
    try:
        print(f"[MIGRATE][INFO] Menjalankan upgrade ke revision '{revision}'...")
        upgrade(revision=revision)
        print(f"[MIGRATE][OK] Upgrade ke '{revision}' berhasil.")
    except Exception:
        print(f"[MIGRATE][ERROR] Gagal upgrade ke revision '{revision}'.")
        print(traceback.format_exc())
        raise RuntimeError(
            f"Gagal menjalankan upgrade ke '{revision}'.\n" + traceback.format_exc()
        )


def run_downgrade(revision: str = "-1") -> None:
    """
    Rollback migrasi ke revision sebelumnya (flask db downgrade).

    Args:
        revision: Target revision. Default '-1' = mundur satu langkah.
                  Gunakan 'base' untuk rollback ke awal.

    Raise:
        RuntimeError jika downgrade gagal.
    """
    try:
        print(f"[MIGRATE][INFO] Menjalankan downgrade ke revision '{revision}'...")
        downgrade(revision=revision)
        print(f"[MIGRATE][OK] Downgrade ke '{revision}' berhasil.")
    except Exception:
        print(f"[MIGRATE][ERROR] Gagal downgrade ke revision '{revision}'.")
        print(traceback.format_exc())
        raise RuntimeError(
            f"Gagal menjalankan downgrade ke '{revision}'.\n" + traceback.format_exc()
        )


def run_current() -> None:
    """
    Tampilkan revision migrasi yang sedang aktif di database (flask db current).
    """
    try:
        print("[MIGRATE][INFO] Mengecek revision migrasi saat ini...")
        current(verbose=True)
    except Exception:
        print("[MIGRATE][ERROR] Gagal mengambil revision migrasi saat ini.")
        print(traceback.format_exc())
        raise RuntimeError(
            "Gagal mengambil revision migrasi saat ini.\n" + traceback.format_exc()
        )


def run_history() -> None:
    """
    Tampilkan riwayat seluruh migrasi yang tersedia (flask db history).
    """
    try:
        print("[MIGRATE][INFO] Mengambil riwayat migrasi...")
        history(verbose=True)
    except Exception:
        print("[MIGRATE][ERROR] Gagal mengambil riwayat migrasi.")
        print(traceback.format_exc())
        raise RuntimeError(
            "Gagal mengambil riwayat migrasi.\n" + traceback.format_exc()
        )


# =============================================================
# ENTRYPOINT UTAMA
# =============================================================

def init_migrate(app) -> None:
    """
    Inisialisasi Flask-Migrate ke Flask app.

    Fungsi ini HANYA mendaftarkan ekstensi Migrate ke app —
    tidak menjalankan migrasi apapun secara otomatis.

    Untuk menjalankan migrasi, gunakan:
        - CLI  : flask db init / migrate / upgrade / downgrade
        - Kode : run_init() / run_migrate() / run_upgrade() / run_downgrade()

    Urutan eksekusi:
        1. Validasi konfigurasi Migrate
        2. Daftarkan ekstensi Flask-Migrate ke app + db

    Args:
        app: Flask application instance (sudah melewati init_database())

    Raise:
        ValueError   : Jika konfigurasi tidak valid.
        RuntimeError : Jika ekstensi gagal diinisialisasi.
    """
    print("=" * 60)
    print("[MIGRATE] Memulai inisialisasi Flask-Migrate...")
    print("=" * 60)

    try:
        # Step 1 — Validasi config
        _validate_migrate_config()

        # Step 2 — Init ekstensi
        _init_migrate_extension(app)

        print("=" * 60)
        print("[MIGRATE][OK] Flask-Migrate berhasil diinisialisasi.")
        print("=" * 60)

    except ValueError as e:
        print(f"[MIGRATE][CRITICAL] Konfigurasi tidak valid: {e}")
        print(traceback.format_exc())
        raise

    except RuntimeError as e:
        print(f"[MIGRATE][CRITICAL] Gagal inisialisasi: {e}")
        print(traceback.format_exc())
        raise

    except Exception as e:
        print(f"[MIGRATE][CRITICAL] Error tidak terduga: {e}")
        print(traceback.format_exc())
        raise