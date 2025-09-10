import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def _flatten_findings(combined: dict) -> list[dict]:
    rows = []
    cloud = combined.get("cloud_scan") or {}
    file_scan = combined.get("file_scan") or {}

    # Cloud
    if cloud:
        rows.append({
            "Section": "Cloud",
            "Item": cloud.get("url", ""),
            "Detail": f"{cloud.get('status','')} (HTTP {cloud.get('http_code','')})",
            "Severity": cloud.get("risk", "Unknown"),
        })

    # File findings
    if file_scan:
        file_name = file_scan.get("file_name", "")
        for f in file_scan.get("findings", []):
            rows.append({
                "Section": "File",
                "Item": file_name,
                "Detail": f"{f['type']} ({f['count']} found)",
                "Severity": file_scan.get("severity", "Low"),
            })
    return rows

def build_csv_report(combined: dict) -> bytes:
    rows = _flatten_findings(combined)
    if not rows:
        rows = [{"Section": "Info", "Item": "-", "Detail": "No issues detected.", "Severity": "Low"}]
    df = pd.DataFrame(rows, columns=["Section", "Item", "Detail", "Severity"])
    return df.to_csv(index=False).encode("utf-8")

def build_pdf_report(combined: dict) -> bytes:
    """
    Returns a PDF bytes object with the summary.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 50, "Cloud Security & Data Leak Report")

    y = height - 90
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "1) Cloud Scan")
    y -= 20
    c.setFont("Helvetica", 11)

    cloud = combined.get("cloud_scan") or {}
    if cloud:
        lines = [
            f"URL: {cloud.get('url','')}",
            f"Status: {cloud.get('status','')} (HTTP {cloud.get('http_code','')})",
            f"Risk: {cloud.get('risk','Unknown')}",
        ]
        for line in lines:
            c.drawString(60, y, line)
            y -= 16
    else:
        c.drawString(60, y, "No cloud scan performed.")
        y -= 16

    # File section
    y -= 12
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "2) File Scan")
    y -= 20
    c.setFont("Helvetica", 11)
    file_scan = combined.get("file_scan") or {}
    if file_scan and file_scan.get("findings"):
        c.drawString(60, y, f"File: {file_scan.get('file_name','')}")
        y -= 16
        c.drawString(60, y, f"Overall Severity: {file_scan.get('severity','Low')}")
        y -= 20
        for f in file_scan["findings"]:
            # handle page break
            if y < 80:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 11)
            c.drawString(60, y, f"- {f['type']}: {f['count']} found")
            y -= 16
            if f.get("samples"):
                c.drawString(80, y, "Samples: " + ", ".join(f["samples"]))
                y -= 16
    else:
        c.drawString(60, y, "No sensitive data found or no file scanned.")
        y -= 16

    # Recommendations
    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "3) Recommendations")
    y -= 20
    c.setFont("Helvetica", 11)
    recs = [
        "• Restrict public access on cloud storage; review bucket/object ACLs.",
        "• Avoid storing Aadhaar/PAN/passwords in plain text; encrypt sensitive data.",
        "• Implement least-privilege IAM roles & enable server-side encryption.",
    ]
    for r in recs:
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)
        c.drawString(60, y, r)
        y -= 16

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
