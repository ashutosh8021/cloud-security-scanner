# Basic regexes for Indian context + common patterns
PATTERNS = {
    # Aadhaar often formatted in 4-4-4 pattern with spaces
    "Aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b",
    # PAN: 5 letters, 4 digits, 1 letter
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "Email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b",
    "Phone": r"\b[6-9]\d{9}\b",
    # Naive password-like pattern: at least 8 chars with letters+digits (and optional specials)
    "Password": r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}",
}
