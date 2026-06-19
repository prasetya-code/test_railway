```json
{
  "Content-Security-Policy": "default-src 'self'",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
  "Cross-Origin-Embedder-Policy": "require-corp",
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Resource-Policy": "same-origin",
  "X-XSS-Protection": "1; mode=block",
  "Expect-CT": "max-age=86400, enforce",
  "Clear-Site-Data": "\"cache\", \"cookies\", \"storage\""
}
```

```py
# Flask implementation
# pip install flask-talisman  (rekomendasi)
from flask_talisman import Talisman
Talisman(app, content_security_policy={'default-src': "'self'"})

# Atau manual via after_request:
@app.after_request
def security_headers(resp):
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return resp
```