```json
{
  "Accept": "application/json",
  "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Charset": "utf-8",
  "TE": "trailers"
}
```

```py
# Flask implementation
@app.route('/api/data')
def data():
    accept = request.headers.get('Accept', '*/*')
    lang   = request.headers.get('Accept-Language', 'en')
    if 'application/json' in accept:
        return jsonify({'lang': lang})
```