# Request Headers (11 kategori) — `dibaca via request.headers.get('...')`

1. General — `Cache-Control, Connection, dll. → dicek di @before_request`
2. Request Context — `Host, User-Agent, Referer → untuk fingerprint client`
3. Content Negotiation — `Accept, Accept-Language → tentukan format response`
4. Authentication — `Authorization: Bearer ... → validasi token`
5. Cookie — `dibaca via request.cookies.get(...)`
6. Conditional — `If-None-Match, If-Modified-Since → implementasi 304 Not Modified`
7. Range — `Range: bytes=0-999 → untuk streaming/download sebagian file`
8. CORS Request — `Origin, Access-Control-Request-Method → preflight handling`
9. Fetch Metadata — `Sec-Fetch-Site, Sec-Fetch-Mode → mitigasi CSRF modern`
10. Client Hints — `Sec-CH-UA-Mobile, Device-Memory → adaptive response`
11. Request Body — `Content-Type, Content-Length → parse payload`


# Response Headers (11 kategori) — `di-set via resp.headers[...] = ... atau @after_request`

1. General — `jarang diset manual, Flask handle otomatis`
2. Server Info — `sembunyikan Server dan X-Powered-By (security best practice)`
3. Response Body — `Content-Type, Content-Language`
4. Cache — `Cache-Control, ETag, Vary → performa & validasi`
5. Redirection — `cukup pakai redirect(), Flask set Location otomatis`
6. Auth Response — `WWW-Authenticate → kembalikan bersama status 401`
7. Cookie — `pakai resp.set_cookie(...) dengan flag httponly, secure, samesite`
8. CORS Response — `Access-Control-Allow-* → gunakan flask-cors untuk kemudahan`
9. Security ⭐ — `paling penting! Gunakan library flask-talisman`
10. Download/File — `Content-Disposition: attachment untuk trigger download`
11. Performance — `Server-Timing → ukur durasi di before_request / after_request`


