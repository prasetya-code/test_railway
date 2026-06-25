# minimal policy web headers yang layak dipasang di production

| Level       | Persentase | Keterangan                                              |
| ----------- | ---------- | ------------------------------------------------------- |
| Basic       | 60-70%     | Sudah aman untuk aplikasi internal                      |
| Recommended | 80-90%     | Cocok untuk mayoritas website dan API production        |
| Hardened    | 95-100%    | Cocok untuk fintech, healthcare, government, enterprise |


# headers

- header param tidak pernah terpanggil, dan harus di panggil lewat regis_utils
- skema yang di inginkan saya mau semua param header di satukan ke dalam satu file dulu yakni headers.py lalu pada regis_utils tingal memanggil init_headers yang menjalankan semua header param yang sudah di set

# Note

- ** itu untuk unpack (membongkar) isi dictionary dan menggabungkannya ke dalam dictionary baru.

> flask talisman yang sudah ada belum menerapkan:
 - CSP dev → REPORT-ONLY (bukan OFF total)
 - COEP hanya aktif di production
 - COOP/CORP tetap aman tapi lebih fleksibel di dev
 - Tambahkan hook security_event() untuk CSP violation (tanpa endpoint baru)
 - Dev mode lebih “debug-friendly” tanpa mengurangi keamanan dasar

> csp
| Error Console Browser            | Tambahkan ke                    |
| -------------------------------- | ------------------------------- |
| `Refused to load the script`     | `script-src`                    |
| `Refused to load the stylesheet` | `style-src`                     |
| `Refused to load the image`      | `img-src`                       |
| `Refused to load the font`       | `font-src`                      |
| `Refused to connect`             | `connect-src`                   |
| `Refused to frame`               | `frame-src` / `frame-ancestors` |


# CORE

🧠 Struktur minimal portfolio yang ideal

Kalau diringkas, stack “clean portfolio Flask”:

✔ Core

- Flask
- Flask-SQLAlchemy

✔ Data / Schema Layer (INI TEMPAT PYDANTIC)

- Pydantic (validation, schema, serialization)
- (opsional) Marshmallow (alternatif Pydantic)

✔ Security

- Flask-Talisman
- Flask-Limiter
- Flask-CORS (jika API)

✔ Performance

- Flask-Compress
- Flask-Caching (opsional)

✔ Auth

- session (Flask built-in) → untuk SSR / render route
- PyJWT → untuk API (stateless auth)