from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

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
        return {
            'jsonData': jsonData,
            'dtnow': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(e)
        return {}