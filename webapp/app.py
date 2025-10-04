from flask import Flask, render_template, jsonify, request
from collections import defaultdict
from datetime import datetime
import csv
import os

app = Flask(__name__)

# 副函式
def get_forex_data(csv_file="rates.csv"):
    data_by_currency = defaultdict(list)
    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                currency = row["幣別"]
                data_by_currency[currency].append([
                    row["銀行"],
                    row["現金買入"],
                    row["現金賣出"],
                    row["即期買入"],
                    row["即期賣出"]
                ])
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

        # 回傳前端期望格式
        jsonData = [{
            "name": forexr.bank_category.get(bank_id, bank_id),
            "rates": records
        }]

         # csv
        csv_file = "rates.csv"
        file_exists = os.path.exists(csv_file)

        with open(csv_file, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            # 如果 CSV 不存在，先寫表頭
            if not file_exists:
                writer.writerow(["銀行", "幣別", "現金買入", "現金賣出", "即期買入", "即期賣出"])
            
            # 寫入資料，每一列加上銀行名稱
            for row in records:
                writer.writerow([forexr.bank_category.get(bank_id, bank_id)] + row)

        return {
            'jsonData': jsonData,
            'dtnow': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        print(e)
        return {}
    


@app.route("/compare")
def compare():
    from collections import defaultdict
    import csv

    # 讀取 CSV，生成字典: {幣別中文: [...資料...]}
    data_by_currency = defaultdict(list)
    try:
        with open("rates.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 只留中文幣別
                currency_name = row["幣別"]
                if any(u'\u4e00' <= c <= u'\u9fff' for c in currency_name):
                    data_by_currency[currency_name].append({
                        "銀行": row["銀行"],
                        "即期買進": row["即期買入"],
                        "即期賣出": row["即期賣出"],
                        "現金買進": row["現金買入"],
                        "現金賣出": row["現金賣出"]
                    })
    except FileNotFoundError:
        pass

    # 下拉選單用 list of tuple (中文幣別, 中文幣別)
    currencies = sorted([(currency, currency) for currency in data_by_currency.keys()])

    return render_template("forex_compare.html", currencies=currencies)

@app.route('/get_currency_rates')
def get_currency_rates():
    currency = request.args.get('currency')
    data_by_currency = defaultdict(list)

    try:
        with open("rates.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["幣別"] == currency:
                    data_by_currency[currency].append({
                        "銀行": row["銀行"],
                        "即期買進": row["即期買入"],
                        "即期賣出": row["即期賣出"],
                        "現金買進": row["現金買入"],
                        "現金賣出": row["現金賣出"]
                    })
    except FileNotFoundError:
        pass

    return jsonify({ "rates": data_by_currency.get(currency, []) })