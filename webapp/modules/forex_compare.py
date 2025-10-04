from flask import Flask, render_template, request
import csv
from collections import defaultdict

app = Flask(__name__)

def get_forex_data(csv_file="rates.csv"):
    # data_by_currency: key=幣別代碼, value=list of [銀行, 現金買入, 現金賣出, 即期買入, 即期賣出]
    data_by_currency = defaultdict(list)
    display_name_map = {}  # 幣別代碼 -> 中文+代碼

    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳過表頭
            for row in reader:
                bank = row[0]
                code = row[1]
                cash_buy = row[2]
                cash_sell = row[3]
                spot_buy = row[4]
                spot_sell = row[5]
                # row[8] 是中文名稱+代碼
                display_name = row[8] if len(row) > 8 else code
                display_name_map[code] = display_name

                data_by_currency[code].append([bank, cash_buy, cash_sell, spot_buy, spot_sell])
    except FileNotFoundError:
        pass

    return data_by_currency, display_name_map

@app.route("/compare")
def compare():
    forex_data, display_name_map = get_forex_data()
    
    # 下拉選單用 (代碼, 中文+代碼)
    currencies = sorted([
        (code, display_name_map.get(code, code))
        for code in forex_data.keys()
    ])

    selected_currency = request.args.get("currency")
    rows = forex_data.get(selected_currency, []) if selected_currency else []

    return render_template("forex_compare.html",
                           currencies=currencies,
                           selected_currency=selected_currency,
                           rows=rows)
