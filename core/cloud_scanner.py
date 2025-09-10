import requests
from urllib.parse import urlparse

def scan_cloud_url(url: str):
    result = {
        "url": url,
        "host": urlparse(url).netloc,
        "status": "Unknown",
        "http_code": None,
        "risk": "Low",
        "notes": []
    }

    try:
        response = requests.get(url, timeout=5)
        result["http_code"] = response.status_code

        if response.status_code == 200:
            # Keywords that usually mean it's a cloud object
            cloud_keywords = [
                "s3", "amazonaws.com", "blob.core.windows.net", "storage.googleapis.com",
                "digitaloceanspaces.com", "aliyuncs.com"
            ]

            if any(word in url.lower() for word in cloud_keywords):
                result["status"] = "Cloud object accessible"
                result["risk"] = "High"
                result["notes"].append("Cloud object is publicly accessible without authentication.")
            else:
                result["status"] = "Website accessible"
                result["risk"] = "Low"
                result["notes"].append("Normal website, not a cloud object.")
        else:
            result["status"] = f"Inaccessible ({response.status_code})"
            result["risk"] = "Low"
            result["notes"].append("The object is not accessible or requires authentication.")

    except requests.exceptions.RequestException as e:
        result["status"] = "Error"
        result["risk"] = "Low"
        result["notes"].append(str(e))

    return result
