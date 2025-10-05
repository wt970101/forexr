from collections import defaultdict
import csv

def get_forex_data(csv_file="rates.csv"):
    data_by_currency = defaultdict(list)
    display_name_map = {}

    try:
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳過表頭

            for row in reader:
                if len(row) < 9:
                    continue  # 跳過不完整的列

                bank = row[0].strip()
                code = row[1].strip()
                cash_buy = row[2].strip()
                cash_sell = row[3].strip()
                spot_buy = row[4].strip()
                spot_sell = row[5].strip()
                display_name = row[8].strip() if len(row) > 8 and row[8].strip() else f"{row[0].strip()}{code}"


                display_name_map[code] = display_name

                data_by_currency[code].append({
                    "銀行": bank,
                    "現金買進": cash_buy,
                    "現金賣出": cash_sell,
                    "即期買進": spot_buy,
                    "即期賣出": spot_sell
                })

    except FileNotFoundError:
        print("⚠️ 找不到 CSV 檔案:", csv_file)

    return data_by_currency, display_name_map
