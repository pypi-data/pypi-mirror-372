from __future__ import annotations

from pathlib import Path
import subprocess
import hashlib
import json
import os

from flask import Flask, render_template, request, jsonify
from platformdirs import user_cache_dir


PKG_NAME = "codecam"


def _cache_file_for(cwd: str) -> Path:
    p = Path(cwd).resolve()
    h = hashlib.sha1(str(p).encode("utf-8")).hexdigest()[:16]
    cache_dir = Path(user_cache_dir(PKG_NAME))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"selected_files_{h}.json"


def create_app(default_path: str = ".") -> Flask:
    app = Flask(__name__, template_folder="templates")

    @app.route("/")
    def index():
        selected_path = _cache_file_for(default_path)
        if selected_path.exists():
            selected_files = json.loads(selected_path.read_text())
        else:
            selected_files = []
        current_directory = str(Path(default_path).resolve())
        return render_template(
            "index.html",
            default_path=default_path,
            selected_files=selected_files,
            current_directory=current_directory,
        )

    @app.route("/browse", methods=["POST"])
    def browse():
        path = request.json.get("path", default_path) or "."
        files = []
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ["venv", "__pycache__", ".git"]]
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return jsonify(files=files)

    @app.route("/generate", methods=["POST"])
    def generate():
        files = request.json.get("files", [])
        result = _generate_snapshot(files)
        _cache_file_for(default_path).write_text(json.dumps(files))
        return jsonify(result=result)

    @app.route("/clone", methods=["POST"])
    def clone_repo():
        repo_url = request.json.get("repo_url")
        clone_dir = request.json.get("clone_dir", "cloned_repo")
        if os.path.exists(clone_dir):
            return jsonify({"stdout": "Repo already exists.", "stderr": "Repo already exists."})
        result = subprocess.run(["git", "clone", repo_url, clone_dir], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"stdout": f"Repository cloned successfully to {clone_dir}.", "stderr": None})
        else:
            return jsonify({"stdout": "Failed to clone repository.", "stderr": result.stderr})

    @app.route("/shutdown", methods=["POST"])
    def shutdown():
        # graceful stop for werkzeug dev server
        fn = request.environ.get("werkzeug.server.shutdown")
        if fn is None:
            # If not running werkzeug (e.g., different server), just exit
            os._exit(0)
        fn()
        return "Server shutting down..."

    def _generate_snapshot(files: list[str] | None) -> str | None:
        if files is None:
            # not used in web path; kept for parity with CLI future use
            sel = _cache_file_for(default_path)
            if not sel.exists():
                return None
            files = json.loads(sel.read_text())
        import platform
        from datetime import datetime
        result = f"System: {platform.system()} {platform.release()} {platform.version()}\nTime: {datetime.now()}\n"
        for f in files:
            if os.path.isdir(f):
                continue
            with open(f, "r") as fh:
                content = fh.read()
            result += f"--- {f} ---\n{content}\n\n"
        return result

    return app
