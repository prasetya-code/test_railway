```json
{
  "Date": "Fri, 19 Jun 2026 10:00:00 GMT",
  "Connection": "keep-alive",
  "Transfer-Encoding": "chunked",
  "Trailer": "Expires",
  "Upgrade": "websocket",
  "Via": "1.1 proxy.example.com",
  "Warning": "199 Miscellaneous warning"
}
```

```py
# Flask implementation
# Flask/Werkzeug menambahkan Date otomatis.
# Untuk Connection dan Via jarang diset manual:
resp = make_response("OK")
resp.headers['Connection'] = 'keep-alive'
return resp
```