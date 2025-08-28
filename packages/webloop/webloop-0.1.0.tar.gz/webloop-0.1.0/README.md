# Webloop

A Flask-inspired Python web framework with:
- Routing
- ORM (SQLite-based)
- Authentication
- NanoHTML (custom HTML syntax)
- Built-in responsive CSS and Tailwind support

## Quickstart

```bash
pip install webloop
```

```python
import webloop

app = webloop.Webloop()

@app.route("/")
def index(req):
    return "Hello from Webloop!"

app.run()
```
