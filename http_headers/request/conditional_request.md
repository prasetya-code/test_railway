```json
{
  "If-Match": "\"etag123\"",
  "If-None-Match": "\"etag456\"",
  "If-Modified-Since": "Wed, 01 Jan 2025 00:00:00 GMT",
  "If-Unmodified-Since": "Thu, 02 Jan 2025 00:00:00 GMT",
  "If-Range": "\"etag789\""
}
```

```py
# Flask implementation
@app.route('/resource')
def resource():
    etag = "abc123"
    if request.headers.get('If-None-Match') == etag:
        return Response(status=304)
    resp = make_response(data)
    resp.headers['ETag'] = etag
    return resp
```