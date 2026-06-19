```json
{
  "Server-Timing": "db;dur=50",
  "Timing-Allow-Origin": "*",
  "NEL": "{\"report_to\":\"default\",\"max_age\":86400}",
  "Report-To": "{\"group\":\"default\",\"max_age\":86400}",
  "Reporting-Endpoints": "default=\"https://report.example.com\""
}
```

```py
# Flask implementation
import time

@app.before_request
def start_timer(): g.start = time.time()

@app.after_request
def add_timing(resp):
    dur = (time.time() - g.start) * 1000
    resp.headers['Server-Timing'] = f'total;dur={dur:.1f}'
    resp.headers['Timing-Allow-Origin'] = '*'
    return resp
```