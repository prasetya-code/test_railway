```json
{
  "Server": "nginx",
  "X-Powered-By": "Node.js"
}
```

```py
# Flask implementation
# Sembunyikan info server (best practice):
@app.after_request
def hide_server(resp):
    resp.headers['Server'] = 'WebServer'
    resp.headers.pop('X-Powered-By', None)
    return resp
```