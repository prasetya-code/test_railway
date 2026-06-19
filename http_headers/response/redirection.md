```json
{
  "Location": "https://example.com/login"
}
```

```py
# Flask implementation
# Flask redirect otomatis set Location:
from flask import redirect, url_for

@app.route('/old')
def old_page():
    return redirect(url_for('new_page'), code=301)
```