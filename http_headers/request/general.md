```json
{
  "Cache-Control": "no-cache",
  "Connection": "keep-alive",
  "Date": "Fri, 19 Jun 2026 10:00:00 GMT",
  "Pragma": "no-cache",
  "Trailer": "Expires",
  "Transfer-Encoding": "chunked",
  "Upgrade": "websocket",
  "Via": "1.1 proxy.example.com",
  "Warning": "199 Miscellaneous warning"
}
```

```py
# Flask implementation
@app.before_request
def check_cache():
    cc = request.headers.get('Cache-Control')
    conn = request.headers.get('Connection')
    # 'no-cache' → jangan gunakan cache
```