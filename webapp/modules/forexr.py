import sys, os
import time
import re
from selenium import webdriver
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def forexr_list(bankid, chrome):
    atable = globals()[bankid](chrome)
    return atable

def get_every_bank_data():
    # ✅ 建立 options 物件
    options = Options()
    options.add_argument("--headless")  # 若要無頭模式可加這行
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ 建立 Chrome driver
    service = Service()
    chrome = webdriver.Chrome(service=service, options=options)

    data = []
    data.append(bot(chrome))
    time.sleep(0.5)
    data.append(cathaybk(chrome))
    data.append(fubon(chrome))
    data.append(esunbank(chrome))
    time.sleep(0.5)
    data.append(yuantabank(chrome))
    data.append(sinopac(chrome))
    data.append(taishinbank(chrome))

    return data

# 靜態爬蟲調整版面
def adjust_layout(atable):

    for i in range(len(atable)):
        for j in range(1, 5):
            try:
                num = float(atable[i][j].strip())
                atable[i][j] = f"{num:.4f}" 
            except:
                atable[i][j] = "-" # 沒有的數據就用 "-" 寫入


        
    return atable

# 動態爬蟲版面調整
def format_table(alist):
    atable = []
    # 統一各家銀行的欄位順序
    for row in alist:
        fcode = []
        fcode.append(re.search('[A-Z]+', row[0]).group()) # 會從中抓出第一個連續的大寫英文字母組成的字串，做為 code
        row = fcode + row[1:]
        atable.append(row)
    return atable


# 台灣銀行
def bot(browser):
    atable = []
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    browser.get(url)
    time.sleep(0.5)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')
    tbody = bsoup.find('tbody')
    time.sleep(0.2)
    tr_list = None
    while tr_list == None:
        tr_list = tbody.find_all('tr') # 做為對每個國家的外幣匯率分類
        time.sleep(0.5)
    for tr in tr_list:
        td_list = tr.find_all('td') # 以各個國家作為分別

        currency = td_list[0].parent.find(
            'div', {'class': 'visible-phone print_hide'}).get_text().strip()  # 各個外幣名稱
        code = currency[-4:-1] # 貨幣代碼

        spot_B = td_list[3].get_text().strip() # 及時買入匯率
        spot_S = td_list[4].get_text().strip() # 及時賣出匯率
        note_B = td_list[1].get_text().strip() # 現金買入匯率
        note_S = td_list[2].get_text().strip() # 現金賣出匯率

        atable.append([code , spot_B, spot_S, note_B, note_S])
        atable = adjust_layout(atable)

    return atable

# 國泰世華
def cathaybk(browser):
    atable = []
    url = "https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    exr_list = bsoup.find_all("div", {"class", "cubre-m-currency__name"}) # 最後一個是空的
    body_list = bsoup.find_all('tbody') 

    for i in range(len(exr_list)-1):
        currency = exr_list[i].get_text().strip()
        code = currency[-3:]

        value_list = body_list[i].find_all('td') # 匯率的比值以 td 做分類
        spot_B = value_list[1].get_text().strip() # 及時買入匯率
        spot_S = value_list[2].get_text().strip() # 及時賣出匯率
        note_B = value_list[7].get_text().strip() # 現金買入匯率
        note_S = value_list[8].get_text().strip() # 現金賣出匯率

        atable.append([code, spot_B, spot_S, note_B, note_S])
        atable = adjust_layout(atable)

    return atable

# 富邦銀行
def fubon(browser):
    atable = []
    url = "https://www.fubon.com/Fubon_Portal/banking/Personal/deposit/exchange_rate/exchange_rate1.jsp"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    body = bsoup.find('tbody')
    time.sleep(0.5) 
    tr_list = body.find_all('tr')
    for tr in tr_list:
        td_list = tr.find_all('td')
        currency = td_list[1].get_text().strip()
        # currency = normalize_currency_name(currency)
        code = currency[-4:-1]

        spot = td_list[3].get_text().strip() 
        spot_B = spot[:7] # 及時買入匯率
        spot_S = spot[-7:] # 及時賣出匯率

        note = td_list[4].get_text().strip()
        note_B = note[:7] # 現金買入匯率
        note_S = note[-7:] # 現金賣出匯率
        atable.append([code, spot_B, spot_S, note_B, note_S])
        atable = adjust_layout(atable)

    return atable

# 玉山銀行
def esunbank(browser):
    atable = []
    url = "https://www.esunbank.com/zh-tw/personal/deposit/rate/forexr/foreign-exchange-rates"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    # 只能找到 code, currency
    # 每個匯率的 class 名稱都不同
    exr_list = bsoup.find_all('td', {'class', "l-exchangeRate__table--title d-block"})

    for exr in exr_list:
        code = exr.find('div', {'class', "col-1 col-lg-2 title-item title-en"}).get_text().strip()
        print(code)

        # 抓出專門放 外匯值 的 list
        value_list = bsoup.find('tr', {'class', "px-3 py-2 p-lg-0 {} currency".format(code)}) # 每個名稱差別在 code 不同
        spot_B = value_list.find('div', {'class', "BBoardRate"}).get_text().strip()
        spot_S = value_list.find('div', {'class', "SBoardRate"}).get_text().strip()
        note_B = value_list.find('div', {'class', "CashBBoardRate"}).get_text().strip()
        note_S = value_list.find('div', {'class', "CashSBoardRate"}).get_text().strip()
        
        atable.append([code, spot_B, spot_S, note_B, note_S])
        atable = adjust_layout(atable)
    return atable


# 元大銀行 
def yuantabank(browser):
    atable = []
    url = "https://www.yuantabank.com.tw/bank/exchangeRate/hostccy.do"
    browser.get(url)
    time.sleep(0.5)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    exr = bsoup.find('table', {'class', "hoverType rate rate_cash"})

    time.sleep(0.2)
    value_list = exr.find_all('tr')

    for value in value_list[1:]:
        category_list = value.find_all('td')

        currency = category_list[0].get_text().strip()
        code = currency[-4:-1]
        spot_B = category_list[1].get_text().strip() # 及時買入匯率
        spot_S = category_list[2].get_text().strip() # 及時賣出匯率
        note_B = category_list[3].get_text().strip() # 現金買入匯率
        note_S = category_list[4].get_text().strip() # 現金賣出匯率

        atable.append([code, spot_B, spot_S, note_B, note_S])
        atable = adjust_layout(atable)
    return atable

# 永豐銀行
def sinopac(browser):
    url = "https://bank.sinopac.com/MMA8/bank/html/rate/bank_ExchangeRate.html"
    browser.get(url)
    time.sleep(1)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')
    tbody = bsoup.find('tbody')
    tr_list = tbody.find_all('tr')
    alist = []
    for tr in tr_list[2:]:
        row = []
        cols = tr.find_all('td')
        for cell in cols:
            row.append(cell.get_text().strip())
        alist.append(row)
    # print(alist)
    return format_table(alist)

# 台新銀行
def taishinbank(browser):
    url = 'https://www.taishinbank.com.tw/TSB/personal/deposit/lookup/realtime/'
    browser.get(url)
    time.sleep(1)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    alist = []
    table = bsoup.find('table', {'class', 'levelone'})
    tr_list = table.find_all('tr', {'class', 'currency'})
    for tr in tr_list:
        currency = tr.get_text().strip()[-3:]
        alist.append([currency])

    table = bsoup.find('table', {'class', 'right'})
    tr_list = table.find_all('tr')
    for i in range(1, len(tr_list)-2):
        td_list = tr_list[i].find_all('td')
        spot_B = td_list[0].get_text().strip()
        spot_B = spot_B[:7]
        spot_S = td_list[1].get_text().strip()
        spot_S = spot_S[:7]
        note_B = td_list[2].get_text().strip()
        note_B = note_B[:7]
        note_S = td_list[3].get_text().strip()
        note_S = note_S[:7]
        
        alist[i-1] += [spot_B, spot_S, note_B, note_S]
    # print(alist)
    return format_table(alist)


# 主函式 
bank_category = {
    'bot': '台灣銀行',
    'fubon': '台北富邦',
    'cathaybk': '國泰世華',
    'esunbank': '玉山銀行', # 有問題
    'yuantabank': '元大銀行',
    'sinopac': '永豐銀行',
    'taishinbank': '台新銀行',
}

if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # ✅ 建立 options 物件
    options = Options()
    options.add_argument("--headless")  # 若要無頭模式可加這行
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ 建立 Chrome driver
    service = Service()
    chrome = webdriver.Chrome(service=service, options=options)

    atable = taishinbank(chrome)
    print("atable", atable)
    print()

    atable = yuantabank(chrome)
    print("atable", atable)
    print()

    atable = sinopac(chrome)
    print("atable", atable)
    print()
 
    chrome.quit()

else: # 以模組方式呼叫本程式的函式
    from webapp.modules.webutils import *
    from webapp.modules.chromed import *
    from webapp.modules.ioutils import *