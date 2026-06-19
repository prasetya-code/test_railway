```json
{
  "Content-Type": "application/json",
  "Content-Length": "512",
  "Content-Encoding": "gzip",
  "Content-Language": "id",
  "Content-Location": "/api/users"
}
```

```py
# Flask implementation
@app.route('/data')
def data():
    resp = make_response(jsonify({"ok": True}))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Content-Language'] = 'id-ID'
    return resp
```