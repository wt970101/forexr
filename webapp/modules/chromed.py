# https://googlechromelabs.github.io/chrome-for-testing/

import platform
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path


# 設定瀏覽器執行參數
options = Options()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# print(BASE_DIR)
system_name = platform.system()

if system_name == 'Windows':

    driver_path = str(BASE_DIR / "driver" / "chromedriver")
    driver_path = str(BASE_DIR / "driver" / "chromedriver-win64")
    service = Service(driver_path)
elif system_name == 'Linux':
    # 下載 Google Chrome 最新穩定版
    # $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

    # 安裝 Google Chrome
    # $ dpkg -i google-chrome-stable_current_amd64.deb
    # $ apt install --fix-broken
    # $ dpkg -i google-chrome-stable_current_amd64.deb

    # 設定中文
    # $ locale-gen zh_TW
    # $ locale-gen zh_TW.UTF-8
    # $ dpkg-reconfigure locales
    # $ update-locale LANG="zh_TW.UTF-8" LANGUAGE="zh_TW"

    # 測試 Google Chrome
    # $ google-chrome --headless --no-sandbox --disable-gpu --print-to-pdf=test.pdf https://www.google.com/
    # $ google-chrome --headless --no-sandbox --disable-gpu --screenshot=test.png https://www.google.com/

    # 確認 Google Chrome 執行檔路徑
    # $ which google-chrome
    options.binary_location = "/usr/bin/google-chrome"

    # 避免錯誤 session not created: DevToolsActivePort file doesn't exist
    options.add_argument("--remote-debugging-port=9222")

    # chromedriver for linux
    service = Service("./chromedriver-linux64")

    # 使 webdriver_manager 自動安裝與系統 Google Chrome 版本相符的 chromedriver
    # from webdriver_manager.chrome import ChromeDriverManager
    # service = Service(ChromeDriverManager().install())

## 取消網頁彈出視窗，避免妨礙網路爬蟲
options.add_argument('--disable-notifications')
# 無頭模式，不開啟瀏覽器視窗程式
options.add_argument("--headless")
# 取消沙箱機制
options.add_argument("--no-sandbox")
# 停用 GPU
options.add_argument("--disable-gpu")
# 停用 /dev/shm 分區
options.add_argument("--disable-dev-shm-usage")
# --disable-3d-apis: GL Driver Message (OpenGL, Performance, GL_CLOSE_PATH_NV, High)
options.add_argument("--disable-3d-apis")

# INFO=0, WARNING=1, LOG_ERROR=2, LOG_FATAL=3 
options.add_argument("--log-level=3") # 訊息
# 關閉 logging 功能
# options.add_experimental_option("excludeSwitches", ["enable-logging"])

if __name__ == '__main__':
    print("直接執行 chromed.py 程式")
else:
    pass
    # print("以模組操作 chromed.py 程式")
    # 可以呼叫裏面的函式、使用變數