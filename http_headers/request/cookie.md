```json
{
  "Cookie": "sessionid=abc123; csrftoken=xyz789"
}
```

```py
# Flask implementation
@app.route('/dashboard')
def dashboard():
    session_id = request.cookies.get('sessionid')
    if not session_id:
        return redirect('/login')
```