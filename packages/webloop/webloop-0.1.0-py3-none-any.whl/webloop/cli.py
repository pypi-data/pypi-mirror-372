import os
import sys
from pathlib import Path

TEMPLATE_APP = """\
from webloop import Webloop, render_nanohtml

app = Webloop()

@app.route("/")
def home(req):
    return render_nanohtml("h1: Hello from Webloop :: p: Built with Webloop! ::")

if __name__ == "__main__":
    app.run()
"""

def new_project(name):
    project_dir = Path(name)
    project_dir.mkdir(parents=True, exist_ok=True)

    # app.py
    (project_dir / "app.py").write_text(TEMPLATE_APP)

    # static + templates folders
    (project_dir / "static").mkdir(exist_ok=True)
    (project_dir / "templates").mkdir(exist_ok=True)

    print(f"✅ Created new Webloop project: {name}")
    print("👉 Run it with: python app.py")

def main():
    if len(sys.argv) < 2:
        print("Usage: webloop new <projectname>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "new" and len(sys.argv) == 3:
        new_project(sys.argv[2])
    else:
        print("Usage: webloop new <projectname>")
