```json
{
  "Range": "bytes=0-1023",
  "If-Range": "\"etag123\""
}
```

```py
# Flask implementation
@app.route('/file')
def download_file():
    range_hdr = request.headers.get('Range')
    # e.g. 'bytes=0-999'
    if range_hdr:
        start, end = parse_range(range_hdr)
        return send_partial(start, end)  # status 206
```