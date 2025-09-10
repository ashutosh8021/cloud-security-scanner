import re
from utils.regex_patterns import PATTERNS
from utils.file_loader import load_text_from_uploaded

SEVERITY_ORDER = {"Low": 1, "Medium": 2, "High": 3}

def _max_severity(a: str, b: str) -> str:
    return a if SEVERITY_ORDER.get(a, 0) >= SEVERITY_ORDER.get(b, 0) else b

def scan_file(uploaded_file) -> dict:
    """
    Extract text from uploaded file, run regex patterns, return matches + severity.
    """
    text = load_text_from_uploaded(uploaded_file)
    findings = []

    for label, pattern in PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.MULTILINE)
        if matches:
            unique = sorted(set(m.strip() if isinstance(m, str) else " ".join(m) for m in matches))
            findings.append({"type": label, "count": len(unique), "samples": unique[:5]})

    # Severity rule of thumb
    severity = "Low"
    if any(f["type"] in ("Aadhaar", "PAN", "Password") for f in findings):
        severity = _max_severity(severity, "High")
    if any(f["type"] in ("Email", "Phone") for f in findings) and severity != "High":
        severity = _max_severity(severity, "Medium")

    return {
        "file_name": getattr(uploaded_file, "name", "uploaded"),
        "total_issue_types": len(findings),
        "severity": severity if findings else "Low",
        "findings": findings,
    }
