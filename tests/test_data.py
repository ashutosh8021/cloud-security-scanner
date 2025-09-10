import io
from core.data_scanner import scan_file

def _mk_upload(name: str, content: bytes):
    f = io.BytesIO(content)
    f.name = name
    return f

def test_scan_file_with_sensitive_data():
    content = b"My Aadhaar is 1234 5678 9012 and email is demo@example.com"
    f = _mk_upload("test.txt", content)
    res = scan_file(f)
    types = {x["type"] for x in res["findings"]}
    assert "Aadhaar" in types
    assert "Email" in types
    assert res["severity"] in {"Medium", "High"}

def test_scan_file_clean():
    content = b"This file has nothing sensitive."
    f = _mk_upload("clean.txt", content)
    res = scan_file(f)
    assert res["severity"] == "Low"
    assert res["findings"] == []
