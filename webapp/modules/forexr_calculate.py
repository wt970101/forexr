import csv

def safe_float(value):
    """安全轉換：把 '-' 或空值變成 0"""
    try:
        if value.strip() in ["", "-", "–", "—"]:
            return 0.0
        return float(value)
    except ValueError:
        return 0.0

def load_rates(csv_file):
    rates = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bank = row["銀行"].strip()
            code = row["幣別代碼"].strip()

            cash_buy = safe_float(row.get("現金買入", "0"))
            cash_sell = safe_float(row.get("現金賣出", "0"))
            spot_buy = safe_float(row.get("即期買入", "0"))
            spot_sell = safe_float(row.get("即期賣出", "0"))

            rates.setdefault(bank, {})[code] = {
                "現金買入": cash_buy,
                "現金賣出": cash_sell,
                "即期買入": spot_buy,
                "即期賣出": spot_sell
            }
    return rates


def calculate_exchange(amount, currency, bank, direction, csv_file="rates.csv"):
    rates = load_rates(csv_file)

    if bank not in rates or currency not in rates[bank]:
        return None  # 沒有找到資料

    rate_info = rates[bank][currency]

    try:
        amount = float(amount)
    except ValueError:
        return None

    # 外幣 ➜ 台幣：用 即期買入
    if direction == "toTWD":
        result = amount * rate_info["即期買入"]
    # 台幣 ➜ 外幣：用 即期賣出
    elif direction == "toForeign":
        result = amount / rate_info["即期賣出"]
    else:
        return None

    return round(result, 2)
