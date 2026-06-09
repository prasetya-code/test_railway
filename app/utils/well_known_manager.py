from config.logging.log_parser import app_logger
from pathlib import Path

import json

logger = app_logger()


# ============================================================
# 🔧 DEFAULT_FILES (Sample Editable dengan variabel version global)
# ============================================================

# Versi global untuk semua file .well-known
# Jika ingin update semua file, cukup ubah angka ini
WELL_KNOWN_VERSION = "1.0.0"

DEFAULT_FILES = {
    # --------------------------------------------------------
    # 1️⃣ security.txt
    # --------------------------------------------------------
    "security.txt": {
        "version": WELL_KNOWN_VERSION,  # versi file global
        "content": (
            "Contact: mailto:your_email@example.com\n"  # email untuk laporan keamanan
            "Encryption: https://yourdomain.com/pgp.txt\n"  # link PGP public key
            "Acknowledgements: https://yourdomain.com/security\n"  # link halaman pengakuan / penghargaan keamanan
            f"# meta_version: {WELL_KNOWN_VERSION}\n"  # meta_version sama dengan version
        ),
    },
    # --------------------------------------------------------
    # 2️⃣ ai-plugin.json
    # --------------------------------------------------------
    "ai-plugin.json": {
        "version": WELL_KNOWN_VERSION,  # versi file
        "content": json.dumps(
            {
                "schema_version": "v1",  # versi skema plugin
                "name_for_human": "My AI Plugin",  # nama plugin untuk manusia
                "name_for_model": "my_ai_plugin",  # nama plugin untuk sistem / model
                "description_for_human": "Deskripsi untuk manusia",  # deskripsi singkat manusia
                "description_for_model": "Deskripsi untuk sistem",  # deskripsi singkat sistem/API
                "auth": {"type": "none"},  # jenis autentikasi API
                "api": {"url": "https://yourdomain.com/api"},  # endpoint API plugin
                "logo_url": "https://yourdomain.com/logo.png",  # logo plugin
                "contact_email": "support@yourdomain.com",  # email support plugin
                "meta_version": WELL_KNOWN_VERSION,  # meta_version sama dengan version
            },
            indent=2,
        ),
    },
    # --------------------------------------------------------
    # 3️⃣ assetlinks.json
    # --------------------------------------------------------
    "assetlinks.json": {
        "version": WELL_KNOWN_VERSION,  # versi file
        "content": json.dumps(
            [
                {
                    "relation": [
                        "delegate_permission/common.handle_all_urls"
                    ],  # hak akses
                    "target": {
                        "namespace": "android_app",  # jenis app (Android)
                        "package_name": "com.example.app",  # nama package Android
                        "sha256_cert_fingerprints": [
                            "AA:BB:CC:DD:EE:FF:..."
                        ],  # fingerprint sertifikat
                    },
                    "meta_version": WELL_KNOWN_VERSION,  # meta_version global
                }
            ],
            indent=2,
        ),
    },
    # --------------------------------------------------------
    # 4️⃣ apple-app-site-association
    # --------------------------------------------------------
    "apple-app-site-association": {
        "version": WELL_KNOWN_VERSION,  # versi file
        "content": json.dumps(
            {
                "applinks": {
                    "apps": [],  # biasanya kosong, hanya format iOS
                    "details": [
                        {
                            "appID": "ABCDE12345.com.example.app",  # Apple App ID
                            "paths": ["*"],  # path yang bisa dibuka di app
                        }
                    ],
                },
                "meta_version": WELL_KNOWN_VERSION,  # meta_version global
            },
            indent=2,
        ),
    },
}


def extract_meta_version(content: str):
    """
    Extract versi meta dari content file JSON atau TXT.
    """
    try:
        data = json.loads(content)
        if isinstance(data, list) and data and "meta_version" in data[0]:
            return data[0]["meta_version"]

        elif isinstance(data, dict) and "meta_version" in data:
            return data["meta_version"]

    except Exception:
        pass

    for line in content.splitlines():
        if "meta_version:" in line:
            return line.split(":")[-1].strip()

    return None


def ensure_well_known(base_dir: Path = None):
    """
    Membuat folder .well-known dan file standar jika belum ada.
    Jika file ada tapi versinya berbeda → backup + update.
    """
    base_dir = Path(base_dir or Path.cwd())

    well_known_dir = base_dir / "app" / "static" / ".well-known"
    well_known_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f".well-known directory ensured at {well_known_dir}")

    for filename, meta in DEFAULT_FILES.items():
        file_path = well_known_dir / filename
        new_version = meta["version"]

        try:
            # Jika file belum ada → buat baru
            if not file_path.exists():
                file_path.write_text(meta["content"], encoding="utf-8")
                logger.info(f"Created .well-known/{filename} (v{new_version})")

                continue

            # Baca content lama
            existing_content = file_path.read_text(encoding="utf-8")
            old_version = extract_meta_version(existing_content)

            # Jika versi berbeda → backup + update
            if old_version != new_version:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                backup_path.write_text(existing_content, encoding="utf-8")

                file_path.write_text(meta["content"], encoding="utf-8")
                logger.warning(
                    f"Updated {filename} → v{new_version} (backup: {backup_path})"
                )

            else:
                logger.debug(f"{filename} already up to date (v{new_version})")

        except Exception as e:
            logger.exception(f"Failed to process {filename}: {e}")
