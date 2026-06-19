```json
{
  "Content-Disposition": "attachment; filename=report.pdf",
  "Accept-Ranges": "bytes",
  "Content-Range": "bytes 0-1023/4096"
}
```

```py
# Flask implementation
@app.route('/download')
def download():
    resp = make_response(open('report.pdf', 'rb').read())
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    resp.headers['Accept-Ranges'] = 'bytes'
    return resp
```