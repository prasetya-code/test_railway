from flask import url_for, current_app
from pathlib import Path


def apply_static_versioning(app_or_bp):
    """
    Fungsi utama untuk menambahkan 'cache control' jangka panjang dan
    mekanisme versi dinamis untuk semua file statis (CSS, JS, gambar, dll).

    Fungsi ini bisa dipanggil baik di level:
      - Flask app utama
      - Blueprint individu

    Tujuannya:
      1. Memastikan browser menyimpan file statis dengan cache panjang (1 tahun)
      2. Otomatis menambahkan query parameter `?v=<timestamp>` agar
         setiap kali file berubah, URL-nya juga berubah — sehingga browser
         akan mengambil versi baru, bukan cache lama.
    """

    # Atur agar browser bisa menyimpan file static
    app_or_bp.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # detik (365 hari)

    # Context processor: menambahkan fungsi custom ke dalam semua template Jinja
    @app_or_bp.context_processor
    def inject_static_version():
        """
        Context processor ini menimpa (override) fungsi url_for default
        di Jinja, untuk menambahkan parameter versi (?v=timestamp) secara otomatis.
        """

        def dated_url_for(endpoint, **values):
            """
            Gantikan url_for biasa, tapi tambahkan versi berdasarkan waktu
            modifikasi file (mtime).
            """
            # Periksa apakah endpoint mengarah ke folder static
            if endpoint.endswith(".static") or endpoint == "static":
                filename = values.get("filename")

                if filename:
                    # Cari folder static yang sesuai dengan endpoint (bisa app atau blueprint)
                    folder = _resolve_static_folder(endpoint)

                    if folder:
                        # Gabungkan path absolut ke file static
                        path = Path(folder) / filename

                        # Jika file benar-benar ada di sistem
                        if path.is_file():
                            # Ambil waktu modifikasi file sebagai "versi"
                            # sehingga URL menjadi /static/css/style.css?v=1731501200
                            values["v"] = _get_mtime(path)

            # Kembalikan hasil url_for asli, tapi sudah ditambahkan ?v=...
            return url_for(endpoint, **values)

        # Daftarkan fungsi ke konteks template Jinja sebagai url_for()
        return dict(url_for=dated_url_for)


def _resolve_static_folder(endpoint):
    """
    Fungsi pembantu untuk mencari path folder static berdasarkan endpoint.

    - Jika endpoint == 'static', berarti file berasal dari app utama.
    - Jika endpoint == 'blueprint_name.static', maka file berasal dari blueprint.
    """

    if endpoint == "static":
        # Ambil folder static milik aplikasi utama
        return current_app.static_folder

    else:
        # Ambil nama blueprint dari endpoint, misalnya 'core.static' -> 'core'
        bp_name = endpoint.split(".", 1)[0]

        # Cari blueprint di dalam registry Flask
        bp = current_app.blueprints.get(bp_name)

        # Jika blueprint ditemukan, ambil properti static_folder-nya
        return getattr(bp, "static_folder", None)


def _get_mtime(path):
    """
    Mengambil waktu modifikasi terakhir (mtime) dari file static.

    Fungsi ini membaca metadata file secara langsung untuk memastikan
    versi selalu berubah ketika file di-build ulang atau dimodifikasi.

    Return:
        int: UNIX timestamp (detik) dari waktu terakhir file diubah
    """
    return int(path.stat().st_mtime)
