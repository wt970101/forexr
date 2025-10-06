
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
from datetime import datetime, timedelta
import csv
import os
import re

app = Flask(__name__)

def get_forex_data(csv_file="rates.csv"):
    data_by_currency = defaultdict(list)

    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_by_currency[row["幣別代碼"]].append({
                    "日期": row["日期"],
                    "銀行": row["銀行"],
                    "現金買進": row["現金買入"],
                    "現金賣出": row["現金賣出"],
                    "即期買進": row["即期買入"],
                    "即期賣出": row["即期賣出"]
                })
    except FileNotFoundError:
        pass

    return data_by_currency

# forexr
@app.route('/')
def forexr():
    return render_template('/forexr.html')

@app.route('/forexr_list/<bank_id>')
def forexr_list(bank_id):
    import webapp.modules.chromed as chromed
    from webapp.modules import forexr
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent
    if chromed.system_name == "Windows":
        driver_path = r"C:\MyApps\forexr\webapp\driver\chromedriver.exe"
        service = Service(driver_path)

    chrome = webdriver.Chrome(chromed.options, service, True)
    atable = forexr.forexr_list(bank_id, chrome)

    try:
        columns, records = forexr.fetch(atable)
        today = datetime.now().strftime("%Y-%m-%d")
        csv_file = "rates.csv"
        fieldnames = ["日期", "銀行", "幣別代碼", "現金買入", "現金賣出", "即期買入", "即期賣出"]

        # 先讀 CSV
        existing_data = []
        if os.path.exists(csv_file):
            with open(csv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)

        # 建立查找索引
        index_map = {(row["日期"], row["銀行"], row["幣別代碼"]): row for row in existing_data}

        # 更新或新增
        for r in records:
            bank_name = forexr.bank_category.get(bank_id, bank_id)
            code = r[0]  # 幣別代碼
            cash_buy, cash_sell, spot_buy, spot_sell = r[1:5]  # 對應欄位
            key = (today, bank_name, code)
            index_map[key] = {
                "日期": today,
                "銀行": bank_name,
                "幣別代碼": code,
                "現金買入": cash_buy,
                "現金賣出": cash_sell,
                "即期買入": spot_buy,
                "即期賣出": spot_sell
            }

        # 寫回 CSV
        with open(csv_file, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in index_map.values():
                writer.writerow(row)
        # =======================================

        # 回傳前端
        jsonData = [{
            "name": forexr.bank_category.get(bank_id, bank_id),
            "rates": records
        }]

        return {
            'jsonData': jsonData,
            'dtnow': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(e)
        return {}
    
@app.route("/compare")
def compare():
    from webapp.modules.forexr_compare import get_forex_data
    forex_data, display_name_map = get_forex_data()
    
    currencies = sorted([
        (code, display_name_map.get(code, code))
        for code in forex_data.keys()
    ])

    selected_currency = request.args.get("currency")
    rows = forex_data.get(selected_currency, []) if selected_currency else []

    return render_template("forexr_compare.html",
                           currencies=currencies,
                           selected_currency=selected_currency,
                           rows=rows)

def get_forex_data(csv_file="rates.csv"):
    data_by_currency = defaultdict(list)

    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row["日期"]
                bank = row["銀行"]
                code = row["幣別代碼"]
                cash_buy = row["現金買入"]
                cash_sell = row["現金賣出"]
                spot_buy = row["即期買入"]
                spot_sell = row["即期賣出"]

                data_by_currency[code].append({
                    "日期": date,
                    "銀行": bank,
                    "現金買進": cash_buy,
                    "現金賣出": cash_sell,
                    "即期買進": spot_buy,
                    "即期賣出": spot_sell
                })
    except FileNotFoundError:
        pass

    return data_by_currency

@app.route("/get_currency_rates")
def get_currency_rates():
    currency = request.args.get("currency")
    if not currency:
        return jsonify({"rates": [], "todayRates": []})

    forex_data = get_forex_data()

    today_str = datetime.now().strftime("%Y-%m-%d")
    five_days_ago = datetime.now() - timedelta(days=5)

    all_rows = forex_data.get(currency, [])

    # 折線圖用：近五天
    recent_rows = [
        row for row in all_rows
        if datetime.strptime(row["日期"], "%Y-%m-%d") >= five_days_ago
    ]

    # 表格用：只取今天的
    today_rows = [
        row for row in all_rows
        if row["日期"] == today_str
    ]

    return jsonify({
        "rates": recent_rows,
        "todayRates": today_rows
    })


from flask import Flask, render_template, request, jsonify
from webapp.modules.forexr_calculate import calculate_exchange

@app.route("/forexr_calculate")
def forexr_calculate_page():
    return render_template("forexr_calculate.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    amount = data.get("amount")
    currency = data.get("currency")
    bank = data.get("bank")
    direction = data.get("direction")

    result = calculate_exchange(amount, currency, bank, direction)

    if result is None:
        return jsonify({"error": "計算失敗或資料不完整"}), 400
    else:
        return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
