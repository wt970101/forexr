from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from webapp.modules.locals import *
import pytz
import smtplib


def send_email(subject, embody, attachments=[], recipient=RECIPIENT_EMAIL):
    # flaskemail of google account
    sender = SENDER_EMAIL
    password = SENDER_PASSWORD
    # email
    content = MIMEMultipart()
    content['subject'] = subject
    content['from'] = sender 
    content['to'] = recipient
    # content.attach(MIMEText('主機時間'))
    content.attach(MIMEText(embody, 'html'))

    with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
        try:
            # 驗證 SMTP 伺服器
            smtp.ehlo()
            # 建立加密傳輸
            smtp.starttls()
            smtp.login(sender, password)
            # 附加 pdf 檔
            for pdf in attachments:
                try:
                    with open(pdf, "rb") as fho:
                        the_pdf = MIMEApplication(fho.read(), _subtype="pdf")
                    the_pdf.add_header('Content-Disposition', 'attachment', filename=str(pdf))
                    content.attach(the_pdf)
                except:
                    print(f"No such file '{pdf}'")
                    pass
            smtp.send_message(content)
        except Exception as e:
            pass

def get_now():
    time_zone = pytz.timezone(TIME_ZONE)
    now = datetime.now(time_zone)
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_nowid():
    time_zone = pytz.timezone(TIME_ZONE)
    now = datetime.now(time_zone)
    return now.strftime("%y%m%d%H%M")

def get_sha2(stext, opt=256):
    import hashlib
    stext = stext.encode('utf8')
    if opt == 256:
        return hashlib.sha256(stext).hexdigest()
    elif opt == 384:
        return hashlib.sha384(stext).hexdigest()
    elif opt == 512:
        return hashlib.sha512(stext).hexdigest()
    return ''


if __name__ == '__main__':
    print('now:', get_now())
    print('nowid:', get_nowid())
    while True:
        print('a. Get Hash   (計算數位指紋)')
        print('b. Send Gmail (寄送電子郵件)')
        print('q. Quit       (離開)')
        op = input('> ').lower()
        if op == 'q':
            break
        elif op == 'a':
            while True:
                stext = input('Text to Hash (q. Quit): ')
                if stext.lower() in ('q', 'quit'):
                    break
                else:
                    print('SHA-256 Hash Value:')
                    print(get_sha2(stext))
                    print()
                        
        elif op == 'b':
            while True:
                embody = input('Email Body (q. Quit): ')
                if embody.lower() in ('q', 'quit'):
                    break
                else:
                    # 輸入要傳送的 pdf 檔案
                    fi = 1
                    attachments = []
                    while True:
                        # 必須設定可以存取到 pdf 的路徑
                        file_pdf = input(f'#{fi} PDF to Attach (empty to end): ')
                        if file_pdf.strip() == '':
                            break
                        attachments.append(file_pdf)
                        fi += 1
                    subject = f'Email Test ({get_now()})'
                    send_email(subject, embody, attachments)
        print()
    