# Tidak perlu ada middleware karena sudah di handle otomatis oleh fl_compress dimana hanya tinggal di inisalisasi saja

from flask_compress import Compress
import traceback


fl_compress = Compress()


def init_compress(app):
    try:
        app.config.setdefault("COMPRESS_ALGORITHM", "gzip")
        # bisa: gzip, br
        # gzip = paling kompatibel (semua browser)
        # br (brotli) = lebih kecil, tapi butuh browser modern

        app.config.setdefault("COMPRESS_LEVEL", 6)
        # 1 = cepat tapi ukuran besar
        # 6 = balance (recommended)
        # 9 = paling kecil tapi berat CPU

        app.config.setdefault("COMPRESS_MIN_SIZE", 500)
        # hanya response >= 500 bytes yang akan dikompres
        # tujuan: menghindari overhead untuk data kecil

        # MIME types yang akan dikompres
        app.config.setdefault(
            "COMPRESS_MIMETYPES",
            [
                "text/html",
                "text/css",
                "text/xml",
                "application/json",
                "application/javascript",
            ],
        )
        # hanya tipe file ini yang dikompres
        # tidak termasuk image/video karena sudah terkompresi secara alami

        # Variasi tambahan
        app.config.setdefault("COMPRESS_REGISTER", True)
        # True = otomatis compress semua response Flask
        # False = harus manual handling

        app.config.setdefault("COMPRESS_BR_LEVEL", 4)
        # Brotli level (kalau pakai br)
        # range 0-11 (4 = balance antara speed & compression)

        # init extension
        fl_compress.init_app(app)

    except Exception as e:
        print(f"[ERROR] init_compress gagal: {e}")
        traceback.print_exc()

        raise
