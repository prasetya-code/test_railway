```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs...",
  "Proxy-Authorization": "Basic dXNlcjpwYXNz"
}
```

```py
# Flask implementation
@app.route('/protected')
def protected():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        abort(401)
    token = auth.split(' ', 1)[1]
    # verify token here
```