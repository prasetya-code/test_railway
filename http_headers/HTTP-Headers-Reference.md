# HTTP Headers Reference

## Overview

HTTP Headers adalah metadata yang dikirim antara **Client** dan **Server** dalam komunikasi HTTP/HTTPS.

Secara umum terdapat dua kelompok utama:

1. **Request Headers** (Client → Server)
2. **Response Headers** (Server → Client)

---

# 1. HTTP Request Headers

Header yang dikirim dari client ke server.

## 1.1 General Headers

Digunakan untuk informasi umum komunikasi HTTP.

| Header            | Fungsi                         |
| ----------------- | ------------------------------ |
| Cache-Control     | Mengontrol cache               |
| Connection        | Mengatur koneksi               |
| Date              | Waktu request dibuat           |
| Pragma            | Legacy cache control           |
| Trailer           | Metadata tambahan setelah body |
| Transfer-Encoding | Chunked encoding               |
| Upgrade           | Upgrade protocol               |
| Via               | Informasi proxy                |
| Warning           | Informasi peringatan           |

### Contoh

```http
Cache-Control: no-cache
Connection: keep-alive
```

---

## 1.2 Request Context Headers

Memberikan konteks tentang client.

| Header     | Fungsi                        |
| ---------- | ----------------------------- |
| Host       | Domain tujuan                 |
| Origin     | Asal request                  |
| Referer    | URL sebelumnya                |
| User-Agent | Identitas browser/client      |
| From       | Email user (jarang digunakan) |

### Contoh

```http
Host: example.com
User-Agent: Mozilla/5.0
Referer: https://google.com
```

---

## 1.3 Content Negotiation Headers

Menjelaskan format yang diterima client.

| Header          | Fungsi                  |
| --------------- | ----------------------- |
| Accept          | MIME Type yang diterima |
| Accept-Language | Bahasa                  |
| Accept-Encoding | Compression             |
| Accept-Charset  | Charset                 |
| TE              | Transfer Encoding       |

### Contoh

```http
Accept: application/json
Accept-Language: id-ID
Accept-Encoding: gzip, br
```

---

## 1.4 Authentication Headers

Digunakan untuk autentikasi.

| Header              | Fungsi            |
| ------------------- | ----------------- |
| Authorization       | Token/Credentials |
| Proxy-Authorization | Auth ke proxy     |

### Contoh

```http
Authorization: Bearer eyJhbGciOi...
```

---

## 1.5 Cookie Headers

| Header | Fungsi                    |
| ------ | ------------------------- |
| Cookie | Mengirim cookie ke server |

### Contoh

```http
Cookie: sessionid=123456
```

---

## 1.6 Conditional Request Headers

Request hanya diproses jika kondisi terpenuhi.

| Header              | Fungsi                |
| ------------------- | --------------------- |
| If-Match            | Berdasarkan ETag      |
| If-None-Match       | Berdasarkan ETag      |
| If-Modified-Since   | Berdasarkan waktu     |
| If-Unmodified-Since | Berdasarkan waktu     |
| If-Range            | Untuk partial content |

### Contoh

```http
If-None-Match: "abc123"
```

---

## 1.7 Range Headers

Untuk meminta sebagian file.

| Header   | Fungsi                    |
| -------- | ------------------------- |
| Range    | Meminta sebagian resource |
| If-Range | Validasi range            |

### Contoh

```http
Range: bytes=0-999
```

---

## 1.8 CORS Request Headers

Digunakan pada Cross-Origin Resource Sharing.

| Header                         | Fungsi                     |
| ------------------------------ | -------------------------- |
| Origin                         | Asal request               |
| Access-Control-Request-Method  | Preflight method           |
| Access-Control-Request-Headers | Header yang akan digunakan |

### Contoh

```http
Origin: https://app.example.com
```

---

## 1.9 Fetch Metadata Headers

Membantu mitigasi serangan Cross-Site.

| Header         | Fungsi          |
| -------------- | --------------- |
| Sec-Fetch-Site | Sumber request  |
| Sec-Fetch-Mode | Mode request    |
| Sec-Fetch-User | User initiated  |
| Sec-Fetch-Dest | Tujuan resource |

### Contoh

```http
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
```

---

## 1.10 Client Hints Headers

Memberikan informasi perangkat dan browser.

| Header             | Fungsi             |
| ------------------ | ------------------ |
| Sec-CH-UA          | Browser            |
| Sec-CH-UA-Mobile   | Mobile             |
| Sec-CH-UA-Platform | OS                 |
| Device-Memory      | RAM                |
| DPR                | Device Pixel Ratio |
| Width              | Resource Width     |
| Viewport-Width     | Lebar viewport     |

### Contoh

```http
Sec-CH-UA: "Chromium"
Sec-CH-UA-Mobile: ?0
```

---

## 1.11 Request Body Headers

Mendeskripsikan isi body request.

| Header           | Fungsi      |
| ---------------- | ----------- |
| Content-Type     | Jenis data  |
| Content-Length   | Ukuran data |
| Content-Encoding | Kompresi    |
| Content-Language | Bahasa      |
| Content-Location | Lokasi data |

### Contoh

```http
Content-Type: application/json
Content-Length: 120
```

---

# 2. HTTP Response Headers

Header yang dikirim dari server ke client.

---

## 2.1 General Response Headers

| Header            | Fungsi            |
| ----------------- | ----------------- |
| Date              | Waktu response    |
| Connection        | Status koneksi    |
| Transfer-Encoding | Encoding          |
| Trailer           | Metadata tambahan |
| Upgrade           | Upgrade protocol  |
| Via               | Informasi proxy   |
| Warning           | Warning message   |

### Contoh

```http
Date: Tue, 15 Jul 2025 10:00:00 GMT
```

---

## 2.2 Server Information Headers

| Header       | Fungsi            |
| ------------ | ----------------- |
| Server       | Nama web server   |
| X-Powered-By | Teknologi backend |

### Contoh

```http
Server: nginx
X-Powered-By: PHP/8.2
```

---

## 2.3 Response Body Headers

| Header           | Fungsi      |
| ---------------- | ----------- |
| Content-Type     | Tipe data   |
| Content-Length   | Ukuran      |
| Content-Encoding | Compression |
| Content-Language | Bahasa      |
| Content-Location | Lokasi data |

### Contoh

```http
Content-Type: application/json
```

---

## 2.4 Cache Headers

Mengontrol cache browser maupun CDN.

| Header        | Fungsi              |
| ------------- | ------------------- |
| Cache-Control | Policy cache        |
| Expires       | Waktu kedaluwarsa   |
| ETag          | Resource identifier |
| Last-Modified | Waktu modifikasi    |
| Age           | Umur cache          |
| Vary          | Variasi cache       |

### Contoh

```http
Cache-Control: max-age=3600
ETag: "abc123"
```

---

## 2.5 Redirection Headers

| Header   | Fungsi          |
| -------- | --------------- |
| Location | Target redirect |

### Contoh

```http
Location: https://example.com/login
```

---

## 2.6 Authentication Headers

| Header             | Fungsi         |
| ------------------ | -------------- |
| WWW-Authenticate   | Challenge auth |
| Proxy-Authenticate | Auth proxy     |

### Contoh

```http
WWW-Authenticate: Basic realm="admin"
```

---

## 2.7 Cookie Headers

| Header     | Fungsi         |
| ---------- | -------------- |
| Set-Cookie | Membuat cookie |

### Contoh

```http
Set-Cookie: sessionid=123; HttpOnly; Secure
```

---

## 2.8 CORS Response Headers

| Header                           | Fungsi                              |
| -------------------------------- | ----------------------------------- |
| Access-Control-Allow-Origin      | Origin yang diizinkan               |
| Access-Control-Allow-Methods     | Method yang diizinkan               |
| Access-Control-Allow-Headers     | Header yang diizinkan               |
| Access-Control-Allow-Credentials | Credential support                  |
| Access-Control-Expose-Headers    | Header yang dapat dibaca JavaScript |
| Access-Control-Max-Age           | Cache preflight                     |

### Contoh

```http
Access-Control-Allow-Origin: *
```

---

## 2.9 Security Headers

Kategori paling penting dalam keamanan aplikasi web.

| Header                       | Fungsi                   |
| ---------------------------- | ------------------------ |
| Content-Security-Policy      | Anti XSS                 |
| Strict-Transport-Security    | Paksa HTTPS              |
| X-Frame-Options              | Anti Clickjacking        |
| X-Content-Type-Options       | Anti MIME Sniffing       |
| Referrer-Policy              | Kontrol Referer          |
| Permissions-Policy           | Kontrol fitur browser    |
| Cross-Origin-Embedder-Policy | COEP                     |
| Cross-Origin-Opener-Policy   | COOP                     |
| Cross-Origin-Resource-Policy | CORP                     |
| X-XSS-Protection             | Legacy XSS Protection    |
| Expect-CT                    | Certificate Transparency |
| Clear-Site-Data              | Hapus data browser       |

### Contoh

```http
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
X-Frame-Options: DENY
```

---

## 2.10 Download/File Headers

| Header              | Fungsi                   |
| ------------------- | ------------------------ |
| Content-Disposition | Download atau inline     |
| Accept-Ranges       | Dukungan partial content |
| Content-Range       | Bagian file              |

### Contoh

```http
Content-Disposition: attachment; filename=report.pdf
```

---

## 2.11 Performance & Monitoring Headers

Digunakan untuk monitoring dan observability.

| Header              | Fungsi                  |
| ------------------- | ----------------------- |
| Server-Timing       | Metrik performa         |
| Timing-Allow-Origin | Izinkan akses timing    |
| NEL                 | Network Error Logging   |
| Report-To           | Endpoint laporan        |
| Reporting-Endpoints | Endpoint reporting baru |

### Contoh

```http
Server-Timing: db;dur=50
```

---

# Ringkasan Kategori

## Request Headers (11 Kategori)

1. General Headers
2. Request Context Headers
3. Content Negotiation Headers
4. Authentication Headers
5. Cookie Headers
6. Conditional Request Headers
7. Range Headers
8. CORS Request Headers
9. Fetch Metadata Headers
10. Client Hints Headers
11. Request Body Headers

---

## Response Headers (11 Kategori)

1. General Response Headers
2. Server Information Headers
3. Response Body Headers
4. Cache Headers
5. Redirection Headers
6. Authentication Headers
7. Cookie Headers
8. CORS Response Headers
9. Security Headers
10. Download/File Headers
11. Performance & Monitoring Headers

---

## Total Kategori

| Jenis                      | Jumlah |
| -------------------------- | ------ |
| Request Header Categories  | 11     |
| Response Header Categories | 11     |
| Total Categories           | 22     |

Dokumen ini dapat digunakan sebagai referensi dasar untuk:

* Web Development
* API Development
* Web Security
* Bug Bounty
* Penetration Testing
* Reverse Engineering HTTP Traffic
* Security Auditing
