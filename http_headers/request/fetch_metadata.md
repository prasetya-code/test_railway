```json
{
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-User": "?1",
  "Sec-Fetch-Dest": "empty"
}
```

```py
# Flask implementation
@app.before_request
def check_fetch_meta():
    site = request.headers.get('Sec-Fetch-Site', '')
    mode = request.headers.get('Sec-Fetch-Mode', '')
    # Tolak cross-site request ke endpoint sensitif
    if site == 'cross-site' and mode == 'navigate':
        abort(403)
```