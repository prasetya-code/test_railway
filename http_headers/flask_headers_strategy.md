# Strategi Penerapan HTTP Headers di Flask

Tidak semua header cocok diterapkan secara global. Berikut panduan lengkap berdasarkan scope dan tipe file.

---

## Pola Arsitektur

```
middleware/
├── global_headers.py      # @after_request untuk semua response
├── api_headers.py         # blueprint /api/*
├── static_headers.py      # per ekstensi file (.js, .css, .png, /sw.js)
└── page_headers.py        # blueprint /admin/*, / (HTML pages)
```

---

## 1. Global — Semua Response

Diterapkan via `@after_request` tanpa pengecualian. Berlaku untuk HTML, JSON, static file, apapun.

### Header yang termasuk

| Header | Nilai | Alasan |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Semua response wajib HTTPS |
| `X-Frame-Options` | `DENY` | Anti-clickjacking berlaku di semua halaman & resource |
| `X-Content-Type-Options` | `nosniff` | Browser tidak boleh sniff MIME apapun |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Konsisten di semua endpoint |
| `Server` | `WebServer` (atau hapus) | Sembunyikan identitas server |
| `X-Powered-By` | _(hapus)_ | Jangan expose stack teknologi |

### Implementasi

```python
# middleware/global_headers.py

GLOBAL_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Server": "WebServer",
}

def init_global_headers(app):
    @app.after_request
    def apply_global_headers(resp):
        for key, val in GLOBAL_HEADERS.items():
            resp.headers[key] = val
        resp.headers.pop("X-Powered-By", None)
        return resp
```

---

## 2. Per Route / Blueprint

Nilainya berbeda tergantung endpoint. Jangan dipukul rata.

### Content-Security-Policy

API JSON tidak butuh `script-src`. Halaman admin punya whitelist berbeda dari halaman publik.

```python
# middleware/page_headers.py

CSP = {
    "default": "default-src 'self'",
    "admin":   "default-src 'self'; script-src 'self' https://cdn.example.com",
    "api":     "default-src 'none'",  # API tidak perlu CSP
}

def init_page_headers(app):
    @app.after_request
    def apply_csp(resp):
        path = request.path
        if path.startswith("/admin"):
            resp.headers["Content-Security-Policy"] = CSP["admin"]
        elif path.startswith("/api"):
            resp.headers["Content-Security-Policy"] = CSP["api"]
        else:
            resp.headers["Content-Security-Policy"] = CSP["default"]
        return resp
```

### Cache-Control (Dinamis)

Endpoint dinamis, auth, dan dashboard tidak boleh di-cache.

```python
NO_CACHE_PREFIXES = ("/api/", "/dashboard", "/admin", "/auth")

@app.after_request
def apply_cache(resp):
    if request.path.startswith(NO_CACHE_PREFIXES):
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        resp.headers.pop("ETag", None)
        resp.headers.pop("Last-Modified", None)
    return resp
```

### CORS Headers

API publik pakai `*`. API private pakai specific origin. Halaman HTML tidak perlu CORS header sama sekali.

```python
# middleware/api_headers.py

CORS_CONFIG = {
    "public":  {"Access-Control-Allow-Origin": "*"},
    "private": {"Access-Control-Allow-Origin": "https://app.example.com",
                "Access-Control-Allow-Credentials": "true"},
}

def init_api_headers(app):
    @app.after_request
    def apply_cors(resp):
        if not request.path.startswith("/api"):
            return resp

        if request.path.startswith("/api/public"):
            cfg = CORS_CONFIG["public"]
        else:
            cfg = CORS_CONFIG["private"]

        for key, val in cfg.items():
            resp.headers[key] = val

        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        resp.headers["Access-Control-Max-Age"] = "86400"
        return resp
```

### Permissions-Policy

Halaman user mungkin butuh kamera/mic. API tidak perlu sama sekali.

```python
PERMISSIONS = {
    "page": "camera=(), microphone=(self), geolocation=()",
    "api":  "camera=(), microphone=(), geolocation=()",
}

@app.after_request
def apply_permissions(resp):
    if request.path.startswith("/api"):
        resp.headers["Permissions-Policy"] = PERMISSIONS["api"]
    else:
        resp.headers["Permissions-Policy"] = PERMISSIONS["page"]
    return resp
```

---

## 3. Per Tipe File

Paling kritikal untuk static assets. Setiap ekstensi punya kebutuhan cache yang berbeda.

### Peta Cache per Tipe File

| Tipe File | Cache-Control | Alasan |
|---|---|---|
| `.js`, `.css` | `public, max-age=31536000, immutable` | Nama file pakai hash (fingerprinting), aman long cache |
| `.png`, `.jpg`, `.svg`, `.webp` | `public, max-age=2592000` | Image jarang berubah, 30 hari cukup |
| `.woff2`, `.ttf` | `public, max-age=31536000, immutable` | Font tidak pernah berubah |
| `.html` | `no-cache` | Selalu validasi ke server |
| `.json` (static) | `public, max-age=3600` | Data semi-statis, 1 jam |
| `/service-worker.js` | `no-cache` | Wajib, SW yang ter-cache tidak bisa diupdate |
| `/manifest.json` | `public, max-age=3600` | PWA manifest |

### Implementasi

```python
# middleware/static_headers.py

import os

STATIC_CACHE = {
    ".js":    "public, max-age=31536000, immutable",
    ".css":   "public, max-age=31536000, immutable",
    ".woff2": "public, max-age=31536000, immutable",
    ".ttf":   "public, max-age=31536000, immutable",
    ".png":   "public, max-age=2592000",
    ".jpg":   "public, max-age=2592000",
    ".jpeg":  "public, max-age=2592000",
    ".webp":  "public, max-age=2592000",
    ".svg":   "public, max-age=2592000",
    ".gif":   "public, max-age=2592000",
    ".ico":   "public, max-age=86400",
    ".html":  "no-cache",
    ".json":  "public, max-age=3600",
}

SPECIAL_FILES = {
    "/service-worker.js": {
        "Cache-Control": "no-cache",
        "Service-Worker-Allowed": "/",
    },
    "/manifest.json": {
        "Cache-Control": "public, max-age=3600",
        "Content-Type": "application/manifest+json",
    },
}

def init_static_headers(app):
    @app.after_request
    def apply_static_headers(resp):
        path = request.path

        # Cek file khusus dulu
        if path in SPECIAL_FILES:
            for key, val in SPECIAL_FILES[path].items():
                resp.headers[key] = val
            return resp

        # Cek berdasarkan ekstensi
        ext = os.path.splitext(path)[1].lower()
        if ext in STATIC_CACHE:
            resp.headers["Cache-Control"] = STATIC_CACHE[ext]

        return resp
```

---

## 4. Kondisional / Khusus

Header yang hanya aktif di kondisi tertentu. Jangan asal enable.

### Server-Timing

Hanya untuk staging/dev atau user internal. Berbahaya jika expose di production publik karena bocorkan info infrastruktur.

```python
import time
from flask import g

@app.before_request
def start_timer():
    g.start_time = time.perf_counter()

@app.after_request
def apply_server_timing(resp):
    if not app.config.get("ENABLE_SERVER_TIMING", False):
        return resp
    dur = (time.perf_counter() - g.start_time) * 1000
    resp.headers["Server-Timing"] = f"total;dur={dur:.1f}"
    resp.headers["Timing-Allow-Origin"] = app.config.get("TIMING_ORIGIN", "*")
    return resp
```

```python
# config.py
class DevelopmentConfig:
    ENABLE_SERVER_TIMING = True
    TIMING_ORIGIN = "*"

class ProductionConfig:
    ENABLE_SERVER_TIMING = False  # Matikan di production
```

### Content-Disposition

Hanya untuk endpoint download. Bukan header global.

```python
@app.route("/download/<filename>")
def download_file(filename):
    resp = make_response(get_file_content(filename))
    resp.headers["Content-Type"] = "application/octet-stream"
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    resp.headers["Accept-Ranges"] = "bytes"
    return resp
```

### COEP / COOP

Hanya untuk halaman yang butuh `SharedArrayBuffer` (misal WebAssembly, multi-threading). Jangan terapkan global karena bisa break embed dari third-party.

```python
ISOLATION_PATHS = ("/app/wasm", "/app/canvas")

@app.after_request
def apply_isolation(resp):
    if request.path.startswith(ISOLATION_PATHS):
        resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return resp
```

### Set-Cookie

Hanya di endpoint login/auth. Flag wajib: `HttpOnly`, `Secure`, `SameSite`.

```python
@app.route("/auth/login", methods=["POST"])
def login():
    # ... validasi credentials ...
    resp = make_response(redirect("/dashboard"))
    resp.set_cookie(
        "session_id",
        value=generate_session_token(),
        httponly=True,
        secure=True,         # Hanya lewat HTTPS
        samesite="Lax",      # Proteksi CSRF
        max_age=3600,
        path="/",
    )
    return resp
```

---

## 5. File Khusus

Beberapa path butuh perlakuan sangat spesifik.

### `/service-worker.js`

```python
@app.route("/service-worker.js")
def service_worker():
    resp = make_response(
        send_from_directory("static", "service-worker.js")
    )
    resp.headers["Cache-Control"] = "no-cache"          # Wajib — jangan pernah cache SW
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Service-Worker-Allowed"] = "/"         # Izinkan SW kontrol semua path
    return resp
```

> **Kenapa `no-cache` untuk Service Worker?**
> Browser cache SW secara agresif. Jika ter-cache dengan `max-age`, update SW tidak akan pernah berjalan sampai cache expired. `no-cache` memaksa browser selalu validasi ke server sebelum menggunakan SW yang tersimpan.

### `/.well-known/*`

```python
@app.route("/.well-known/<path:filename>")
def well_known(filename):
    resp = make_response(
        send_from_directory(".well-known", filename)
    )
    resp.headers["Access-Control-Allow-Origin"] = "*"   # CORS open
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp
```

---

## 6. Struktur Lengkap & Registrasi

```python
# app.py
from flask import Flask
from middleware.global_headers import init_global_headers
from middleware.api_headers import init_api_headers
from middleware.static_headers import init_static_headers
from middleware.page_headers import init_page_headers

def create_app(config_name="production"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Urutan registrasi penting — dieksekusi LIFO (last in, first out)
    init_global_headers(app)   # Dieksekusi paling akhir  → header global selalu ada
    init_page_headers(app)     # CSP, Permissions-Policy
    init_api_headers(app)      # CORS
    init_static_headers(app)   # Cache per tipe file

    return app
```

---

## Ringkasan

| Scope | Contoh Header | Cara Implementasi |
|---|---|---|
| **Global** | HSTS, X-Frame-Options, X-Content-Type-Options | `@after_request` di `create_app` |
| **Per route** | CSP, Permissions-Policy, Cache no-store, CORS | `@after_request` dengan cek `request.path` |
| **Per tipe file** | Cache-Control max-age, ETag | Cek `os.path.splitext(request.path)` |
| **Kondisional** | Server-Timing, COEP/COOP | Cek config flag atau path prefix |
| **Khusus** | Set-Cookie, Content-Disposition, Service-Worker-Allowed | Langsung di route handler |