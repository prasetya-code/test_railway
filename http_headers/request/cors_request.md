```json
{
  "Origin": "https://app.example.com",
  "Access-Control-Request-Method": "POST",
  "Access-Control-Request-Headers": "Authorization, Content-Type"
}
```

```py
# Flask implementation
# pip install flask-cors
from flask_cors import CORS
CORS(app, origins=["https://app.example.com"])

# Atau manual:
@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
```