```json
{
  "Access-Control-Allow-Origin": "https://app.example.com",
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Allow-Credentials": "true",
  "Access-Control-Expose-Headers": "X-Request-ID",
  "Access-Control-Max-Age": "86400"
}
```

```py
# Flask implementation
@app.after_request
def cors_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = 'https://app.example.com'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    resp.headers['Access-Control-Max-Age'] = '86400'
    return resp
```