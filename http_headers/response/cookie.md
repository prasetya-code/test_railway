```json
{
  "Set-Cookie": "sessionid=abc123; Secure; HttpOnly; SameSite=Strict"
}
```

```py
# Flask implementation
@app.route('/login', methods=['POST'])
def login():
    resp = make_response(redirect('/dashboard'))
    resp.set_cookie(
        'sessionid', 'token123',
        httponly=True, secure=True,
        samesite='Lax', max_age=3600
    )
    return resp
```