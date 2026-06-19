```json
{
  "Sec-CH-UA": "\"Chromium\";v=\"126\"",
  "Sec-CH-UA-Mobile": "?0",
  "Sec-CH-UA-Platform": "\"Windows\"",
  "Device-Memory": "8",
  "DPR": "2",
  "Width": "1920",
  "Viewport-Width": "1920"
}
```

```py
# Flask implementation
@app.route('/')
def index():
    is_mobile = request.headers.get('Sec-CH-UA-Mobile', '?0') == '?1'
    platform  = request.headers.get('Sec-CH-UA-Platform')
    # Serve mobile template if is_mobile
```