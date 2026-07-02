
import re
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str = ""


class InvoiceData(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


def extract_date(text):
    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if match:
        return match.group(0)
    return ""


def extract_currency(text):
    match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    if "$" in text:
        return "USD"
    if "EUR" in text.upper():
        return "EUR"
    if "GBP" in text.upper():
        return "GBP"
    return ""


def extract_amount(text):
    patterns = [
        r"(?:Total Due|Amount Due|Total|Amount|Balance Due)\s*[:\-]?\s*[\$]?\s*([0-9,]+\.?[0-9]*)",
        r"\$\s*([0-9,]+\.?[0-9]*)",
        r"([0-9,]+\.[0-9]{2})",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            num_str = match.group(1).replace(",", "")
            try:
                return float(num_str)
            except ValueError:
                continue
    return 0.0


def extract_vendor(text):
    labeled_patterns = [
        r"(?:Vendor|From|Bill From|Seller|Company|Billed By|Payable To)\s*[:\-]\s*([^\n,]+)",
    ]
    for pat in labeled_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(".")

    company_pattern = r"([A-Z][A-Za-z0-9\-]*(?:\s+[A-Z][A-Za-z0-9\-]*)*\s+(?:Industries|Ltd|Inc|LLC|Corp|Company|Co|Group|Enterprises))"
    match = re.search(company_pattern, text)
    if match:
        return match.group(1).strip()

    return ""


@app.post("/extract", response_model=InvoiceData)
async def extract(request: ExtractRequest):
    text = request.text or ""

    if not text.strip():
        return InvoiceData(vendor="", amount=0.0, currency="", date="")

    try:
        vendor = extract_vendor(text)
        amount = extract_amount(text)
        currency = extract_currency(text)
        date = extract_date(text)
        return InvoiceData(vendor=vendor, amount=amount, currency=currency, date=date)
    except Exception:
        return InvoiceData(vendor="", amount=0.0, currency="", date="")
