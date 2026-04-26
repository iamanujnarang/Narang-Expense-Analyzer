import pdfplumber
import pandas as pd

def categorize(d):
    d = d.lower()
    if "zepto" in d or "dominos" in d: return "Food"
    if "fuel" in d or "petrol" in d: return "Fuel"
    if "railway" in d: return "Travel"
    if "amazon" in d or "retail" in d: return "Shopping"
    if "jio" in d or "airtel" in d: return "Bills"
    if "sip" in d or "groww" in d: return "Investments"
    if "loan" in d: return "EMI"
    return "Misc"

def extract(file):
    rows = []
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text = p.extract_text()
            if not text: continue
            for line in text.split("\n"):
                parts = line.split()
                if len(parts) > 4:
                    try:
                        amt = float(parts[-2].replace(",", ""))
                        desc = " ".join(parts[1:-3])
                        rows.append([desc, amt, categorize(desc)])
                    except:
                        pass
    return pd.DataFrame(rows, columns=["desc","amt","cat"])