import pytz
from datetime import datetime, timedelta

TIME_ZONE = 'Asia/Taipei'
divider = '-'*40

def get_now(flag=None):
    time_zone = pytz.timezone(TIME_ZONE)
    now = datetime.now(time_zone)
    if flag is None:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    return now

def get_today():
    now = get_now(True)
    return now.strftime("%Y-%m-%d")

def get_prev_day(d=-1):
    now = get_now(True)
    prev_day = now + timedelta(days=d)
    return prev_day.strftime("%Y-%m-%d")

def save_html(filename, html):
    fho = open(filename, 'wt', encoding='utf-8')
    # print(html.prettify(), file=fho)
    fho.close()

def real_price(price):
    return float(price.replace('$', '').replace(',', ''))
    