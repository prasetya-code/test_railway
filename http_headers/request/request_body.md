```json
{
  "Content-Type": "application/json",
  "Content-Length": "256",
  "Content-Encoding": "gzip",
  "Content-Language": "id",
  "Content-Location": "/api/users"
}
```

```py
# Flask implementation
@app.route('/upload', methods=['POST'])
def upload():
    ct = request.headers.get('Content-Type', '')
    if 'application/json' in ct:
        payload = request.get_json()
    elif 'multipart/form-data' in ct:
        file = request.files.get('file')
```