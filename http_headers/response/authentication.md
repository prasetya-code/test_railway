```json
{
  "WWW-Authenticate": "Bearer realm=\"api\"",
  "Proxy-Authenticate": "Basic realm=\"proxy\""
}
```

```py
# Flask implementation
@app.route('/secure')
def secure():
    resp = make_response('Unauthorized', 401)
    resp.headers['WWW-Authenticate'] = 'Bearer realm="api"'
    return resp
```