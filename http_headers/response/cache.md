```json
{
  "Cache-Control": "public, max-age=3600",
  "Expires": "Fri, 19 Jun 2026 11:00:00 GMT",
  "ETag": "\"abc123etag\"",
  "Last-Modified": "Fri, 19 Jun 2026 09:00:00 GMT",
  "Age": "300",
  "Vary": "Accept-Encoding"
}
```

```py
# Flask implementation
@app.route('/static-data')
def static_data():
    resp = make_response(data)
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    resp.headers['ETag'] = '"abc123"'
    resp.headers['Vary'] = 'Accept-Encoding'
    return resp
```