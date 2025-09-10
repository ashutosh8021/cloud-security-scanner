from core.cloud_scanner import scan_cloud_url

def test_scan_cloud_url_fields():
    res = scan_cloud_url("https://example.com")
    # Ensure all expected keys exist
    for key in ("url", "host", "status", "http_code", "risk", "notes"):
        assert key in res

def test_scan_cloud_url_risk_value():
    res = scan_cloud_url("https://example.com")
    assert res["risk"] in {"Low", "Medium", "High", "Unknown"}
