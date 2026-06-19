```json
{
  "Host": "api.example.com",
  "Origin": "https://app.example.com",
  "Referer": "https://app.example.com/dashboard",
  "User-Agent": "Mozilla/5.0",
  "From": "user@example.com"
}
```

```py
# Flask implementation
@app.route('/')
def index():
    host = request.headers.get('Host')
    ua   = request.headers.get('User-Agent')
    ref  = request.headers.get('Referer')
    # block bot: if 'bot' in ua.lower(): abort(403)
```