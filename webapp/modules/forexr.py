import time
import re
from selenium import webdriver
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def forexr_list(bankid, chrome):
    atable = globals()[bankid](chrome)
    return atable

# 統一幣別格式
# def normalize_currency_name(raw_name):
#     """
#     將幣別名稱統一為 '中文名+代碼' 格式
#     """
#     if not raw_name:
#         return ""

#     # 去掉全形/半形空白
#     name = re.sub(r'\s+', '', raw_name)

#     # 第一步：抓英文代碼 (3 碼大寫字母)
#     match = re.search(r'([A-Z]{3})', name)
#     code = match.group(1) if match else ""

#     # 第二步：去掉 (XXX) 這種括號（含代碼）
#     chinese_name = re.sub(r'\([A-Z]{3}\)', '', name)

#     # 第三步：去掉殘留的英文代碼
#     chinese_name = re.sub(r'[A-Z]{3}', '', chinese_name)

#     # 第四步：組合
#     if code:
#         return f"{chinese_name}{code}"
#     else:
#         return chinese_name


def fetch(atable):
    columns = ['Currency', 'Spot(B)', 'Spot(S)', 'Note(B)', 'Note(S)']
    
    for i in range(len(atable)):
        for j in range(1, 5):
            try:
                word = float(atable[i][j].strip())
            except:
                atable[i][j] = "-"
            

    return columns, atable

# 台灣
def bot(browser):
    atable = []
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    browser.get(url)
    time.sleep(0.5)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    body_list = bsoup.find('tbody')
    tr_list = body_list.find_all('tr') # 做為對每個國家的外幣匯率分類
    for tr in tr_list:
        td_list = tr.find_all('td') # 以各個國家作為分別

        currency = td_list[0].parent.find(
            'div', {'class': 'visible-phone print_hide'}).get_text().strip()  # 各個外幣名稱
        # currency = normalize_currency_name(currency)
        code = currency[-4:-1] # 貨幣代碼

        spot_B = td_list[3].get_text().strip() # 及時買入匯率
        spot_S = td_list[4].get_text().strip() # 及時賣出匯率
        note_B = td_list[1].get_text().strip() # 現金買入匯率
        note_S = td_list[2].get_text().strip() # 現金賣出匯率

        atable.append([code , spot_B, spot_S, note_B, note_S])

    return atable

# 國泰世華
def cathaybk(browser):
    atable = []
    url = "https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    exr_list = bsoup.find_all("div", {"class", "cubre-m-currency__name"}) # 最後一個是空的
    body_list = bsoup.find_all('tbody') 
    # print(len(body_list), len(exr_list))

    for i in range(len(exr_list)-1):
        currency = exr_list[i].get_text().strip()
        # currency = normalize_currency_name(currency)
        code = currency[-3:]

        value_list = body_list[i].find_all('td') # 匯率的比值以 td 做分類
        spot_B = value_list[1].get_text().strip() # 及時買入匯率
        spot_S = value_list[2].get_text().strip() # 及時賣出匯率
        digi_B = value_list[4].get_text().strip() # 數位買入匯率
        digi_S = value_list[5].get_text().strip() # 數位賣出匯率
        note_B = value_list[7].get_text().strip() # 現金買入匯率
        note_S = value_list[8].get_text().strip() # 現金賣出匯率

        atable.append([code, spot_B, spot_S, digi_B, digi_S, note_B, note_S])

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
    return atable

# 玉山銀行
def esunbank(browser):
    atable = []
    url = "https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    # 只能找到 code, currency
    # 每個匯率的 class 名稱都不同
    exr_list = bsoup.find_all('td', {'class', "l-exchangeRate__table--title d-block"})

    for exr in exr_list:
        code = exr.find('div', {'class', "col-1 col-lg-2 title-item title-en"}).get_text().strip()
        # currency = exr.find('div', {'class', "col-auto px-3 col-lg-5 title-item"}).get_text().strip() + code
        # currency = normalize_currency_name(currency)

        # 抓出專門放 外匯值 的 list
        value_list = bsoup.find('tr', {'class', "px-3 py-2 p-lg-0 {} currency".format(code)}) # 每個名稱差別在 code 不同
        spot_B = value_list.find('div', {'class', "BBoardRate"}).get_text().strip()
        spot_S = value_list.find('div', {'class', "SBoardRate"}).get_text().strip()
        note_B = value_list.find('div', {'class', "CashBBoardRate"}).get_text().strip()
        note_S = value_list.find('div', {'class', "CashSBoardRate"}).get_text().strip()
        
        atable.append([code, spot_B, spot_S, note_B, note_S])
    return atable


# 元大銀行 
def yuantabank(browser):
    atable = []
    url = "https://www.yuantabank.com.tw/bank/exchangeRate/hostccy.do"
    browser.get(url)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    exr = bsoup.find('table', {'class', "hoverType rate rate_cash"})

    value_list = exr.find_all('tr')

    for value in value_list[1:]:
        category_list = value.find_all('td')

        currency = category_list[0].get_text().strip()
        # currency = normalize_currency_name(currency)
        code = currency[-4:-1]
        spot_B = category_list[1].get_text().strip() # 及時買入匯率
        spot_S = category_list[2].get_text().strip() # 及時賣出匯率
        note_B = category_list[3].get_text().strip() # 現金買入匯率
        note_S = category_list[4].get_text().strip() # 現金賣出匯率

        atable.append([code, spot_B, spot_S, note_B, note_S])
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
        currency = tr.get_text().strip()
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

    return format_table(alist)

def format_table(alist): # 僅限動態匯率
    atable = []
    # 統一各家銀行的欄位順序
    for row in alist:
        fcode = []
        # currency = normalize_currency_name(row[0])
        fcode.append(re.search('[A-Z]+', row[0]).group()) # 會從中抓出第一個連續的大寫英文字母組成的字串，做為 code
        row = fcode + row
        atable.append(row)
    return atable

##########
# 主函式 #

bank_category = {
    'bot': '台灣銀行',
    'fubon': '台北富邦',
    'cathaybk': '國泰世華',
    'esunbank': '玉山銀行',
    'yuantabank': '元大銀行',
    'sinopac': '永豐銀行',
    'taishinbank': '台新銀行',
    'all': '', 
    'quit': ''
    }

if __name__ == '__main__': # 直接以命令方式執行本程式
    from webutils import *
    from chromed import *
    from ioutils import *
    chrome = webdriver.Chrome(options, service, True) # 呼叫 chrome
    bank_keys = list(bank_category.keys())

    while True:
        # 印出選項指令
        i = 1
        for key in bank_keys[:-2]:
            print("{}. {:<13}{}".format(i, key, bank_category[key]))
            i += 1
        print("{}. {:<13}{}".format("a", 'all', bank_category['all']))
        print("{}. {:<13}{}".format("q", 'quit', bank_category['quit']))

        a = (input("要查詢外匯的銀行編號: "))
        if a == 'a': # all
            for key in bank_keys[:-2]:
                t1 = time.perf_counter()
                atable = globals()[key](chrome)
                t2 = time.perf_counter()
        elif a == 'q': # quit
            break
        else: # 其他單選選項
            my_bank = bank_keys[int(a)-1]
            t1 = time.perf_counter() # 計算到當時程式所執行的時間
            atable = globals()[my_bank](chrome)
            # for alist in atable:
            #     print(*alist)
            t2 = time.perf_counter()

    chrome.quit()

else: # 以模組方式呼叫本程式的函式
    from webapp.modules.webutils import *
    from webapp.modules.chromed import *
    from webapp.modules.ioutils import *