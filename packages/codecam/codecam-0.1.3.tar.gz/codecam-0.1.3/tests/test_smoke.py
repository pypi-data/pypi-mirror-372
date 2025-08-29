from __future__ import annotations

from pathlib import Path

from codecam.web import create_app


def test_index_runs() -> None:
    app = create_app(".")
    client = app.test_client()
    rv = client.get("/")
    assert rv.status_code == 200


def test_browse_and_generate(tmp_path: Path) -> None:
    # Arrange: make a file
    f = tmp_path / "hello.txt"
    f.write_text("hi")

    app = create_app(str(tmp_path))
    client = app.test_client()

    # Browse should list the file
    rv = client.post("/browse", json={"path": str(tmp_path)})
    assert rv.status_code == 200
    files = rv.get_json()["files"]
    assert f.as_posix() in files

    # Generate should include its content
    rv = client.post("/generate", json={"files": [f.as_posix()]})
    assert rv.status_code == 200
    body = rv.get_json()["result"]
    assert "hi" in body
    assert "hello.txt" in body
