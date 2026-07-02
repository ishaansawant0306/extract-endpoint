import re
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str = ""


class InvoiceData(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}


def extract_date(text: str) -> str:
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        return m.group(0)
    return ""


def extract_currency(text: str) -> str:
    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    for sym, code in CURRENCY_SYMBOLS.items():
        if sym in text:
            return code
    return ""


def extract_amount(text: str) -> float:
    patterns = [
        r"(?:Total Due|Amount Due|Total|Amount|Balance Due|Due)\s*[:\-]?\s*[\$€£]?\s*([\d,]+\.?\d*)\s*(?:USD|EUR|GBP)?",
        r"[\$€£]\s*([\d,]+\.?\d*)",
        r"([\d,]+\.\d{2})\s*(?:USD|EUR|GBP)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            num_str = m.group(1).replace(",", "")
            try:
                return float(num_str)
            except ValueError:
                continue
    return 0.0


def extract_vendor(text: str) -> str:
    labeled_patterns = [
        r"(?:Vendor|From|Bill From|Seller|Company|Billed By|Payable To)\s*[:\-]\s*([^\n,]+)",
    ]
    for pat in labeled_patterns:
        m =
