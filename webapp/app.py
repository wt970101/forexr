
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
from webapp.modules import amaindb
from datetime import datetime, timedelta, date
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
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent

    try:
        print("得到資訊搜尋", bank_id)
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        mainDB = amaindb.MAINDB()
        print("開始讀寫 firebase")
        data = mainDB.forexr_data_read(bank_id, today_str)
        print("讀取資料完畢")
        bank_category = {
            'bot': '台灣銀行',
            'fubon': '台北富邦',
            'cathaybk': '國泰世華',
            'esunbank': '玉山銀行',
            'yuantabank': '元大銀行',
            'sinopac': '永豐銀行',
            'taishinbank': '台新銀行',
        }
        
        records = []
        for currency, rates in data.items():
            records.append([
                currency,                 # 幣別
                rates['spot_B'],          # 即期買進
                rates['spot_S'],          # 即期賣出
                rates['note_B'],          # 現金買進
                rates['note_S']           # 現金賣出
            ])

        jsondata = [{
            "name": bank_category[bank_id],
            "rates": records

        }]
        print("回傳前端")
        return {
            'jsonData': jsondata,
            'dtnow': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(e)
        return {}
    
@app.route("/compare")
def compare():
    return render_template("forexr_compare.html")

@app.route("/get_currency_rates")
def get_currency_rates():
    currency = request.args.get("currency")
    if not currency:
        return jsonify({"rates": [], "todayRates": []})
    
    mainDB = amaindb.MAINDB()
    today_str = datetime.now().strftime("%Y-%m-%d")
    five_days_ago = datetime.now() - timedelta(days=7)

    bank_category = {
        'bot': '台灣銀行',
        'fubon': '台北富邦',
        'cathaybk': '國泰世華',
        'esunbank': '玉山銀行',
        'yuantabank': '元大銀行',
        'sinopac': '永豐銀行',
        'taishinbank': '台新銀行',
    }

    all_data = []
    ago_data = []
    for bank_code, bank_name in bank_category.items():
        data = mainDB.forexr_data_read(bank_code, today_str)
        print(f"讀取 {bank_name} 資料完畢")
        if data == None:
            print("沒有數據資料")
            continue
        if data[currency] == None:
            print(f"沒有 {currency} 資料")
            continue
        
        row = data[currency]
        data["day"] = today_str
        row["bank_name"] = bank_name
        all_data.append(row)

    for bank_code, bank_name in bank_category.items():
        for i in range(7, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            data = mainDB.forexr_data_read(bank_code, date_str)
            print(f"讀取 {bank_name} 資料完畢")
            if data == None:
                print("沒有數據資料")
                continue
            if data[currency] == None:
                print(f"沒有 {currency} 資料")
                continue
        
            row = data[currency]
            row["bank_name"] = bank_name
            row["date"] = date_str
            ago_data.append(row)

    return jsonify({
        "rates": ago_data,      # 折線圖用（近幾天）
        "todayRates": all_data  # 表格用（今天）
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