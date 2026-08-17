BANK_CODES = {
    "SBIN": "State Bank of India",
    "HDFC": "HDFC Bank",
    "ICIC": "ICICI Bank",
    "PUNB": "Punjab National Bank",
    "CBIN": "Central Bank of India",
    "UTIB": "Axis Bank",
    "BARB": "Bank of Baroda",
    "BKID": "Bank of India",
    "CNRB": "Canara Bank",
    "UBIN": "Union Bank of India",
    "IDIB": "Indian Bank",
    "IOBA": "Indian Overseas Bank",
    "IDFB": "IDFC FIRST Bank",
    "YESB": "YES Bank",
    "KKBK": "Kotak Mahindra Bank",
    "INDB": "IndusInd Bank",
    "RATN": "RBL Bank",
    "FDRL": "Federal Bank",
    "ESFB": "Equitas Small Finance Bank",
    "AUBL": "AU Small Finance Bank",
    "IPOS": "India Post Payments Bank",
    "UTBI": "United Bank of India",
    "UJVN": "Ujjivan Small Finance Bank",
    "FINO": "Fino Payments Bank",
    "BDBL": "Bandhan Bank",
}

def get_bank_name(ifsc):
    if not ifsc:
        return "-"

    ifsc = ifsc.upper()

    if len(ifsc) < 4:
        return "Unknown"

    return BANK_CODES.get(ifsc[:4], "Unknown")