from firebase_admin import credentials
from firebase_admin import db
from flask import Flask
import firebase_admin
from datetime import date
import os


app = Flask(__name__)

class MAINDB():
    def __init__(self):
        dbkey = os.path.join(app.root_path, 'firebase-dbkey.json') # 找到 firebase 的 key
        dburl = 'https://timapp-2008-default-rtdb.asia-southeast1.firebasedatabase.app/'
        try:
            cred = credentials.Certificate(dbkey)
            firebase_admin.initialize_app(cred, {'databaseURL': dburl})
        except:
            pass
        self.ref = db.reference()
    
    def weather_data_add(self, discord_id, num):
        import bot.modules.weather
        print("得到資訊並啟動爬蟲")
        data, city, message = bot.modules.weather._get_city_weather(num)
        achild = self.ref.child(f'discord_weather/{discord_id}')

        achild.set(message)
        adict = {}
        for i, row in enumerate(data):
            # data[i] <=> row
            adict = {
                'date': row[0],
                'temp1': row[1],
                'temp2': row[2],
                'temp3': row[3],
                'ultraviolet': row[4]
                }         
            data[i] = adict

        achild.set([city, message, data])
        print("上傳 firebase 完畢")

    def weather_data_read(self, discord_id):
        achild = self.ref.child(f'discord_weather/{discord_id}')
        print(achild.get())
        return achild.get()
    
    def forexr_data_add(self):
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        """
        銀行名稱
            |- 幣別
            |- ...
        """
        data = forexr.get_every_bank_data()
        bank_names = ['bot', 'fubon', 'cathaybk', 'esunbank', 'yuantabank', 'sinopac', 'taishinbank']
        for ri in range(7):
            print(data[ri])
            for row in data[ri]:
                achild = self.ref.child(f'forexr_rate/{bank_names[ri]}/{today_str}/{row[0]}')
                data[ri] = {
                    "spot_B": row[1], 
                    "spot_S": row[2],
                    "note_B": row[3],
                    "note_S": row[4]
                }

                achild.set(data[ri])

    def forexr_data_read(self, bank_name, time):
        achild = self.ref.child(f'forexr_rate/{bank_name}/{time}')
        print(achild.get())
        return achild.get()

if __name__ == '__main__':
    import forexr
    mainDB = MAINDB()
    op = input("1.add_forexr 2.read_forexr 3.print forexr data: ")
    if op == '1':
        mainDB.forexr_data_add()
        print("上傳成功")
    elif op == '2':
        mainDB.forexr_data_read("bot", "2025-11-04")
    elif op == '3':
        data = forexr.get_every_bank_data()
        print(len(data))

        # print(data)