import threading
import runpy
import sys
import time
from datetime import datetime, timedelta
import tg_bot
from tg_bot import main_channel_lots, lots_bet, ready_lots
from sql_request import db
import schedule 
import doc_gen


def tg():
    runpy.run_module('tg_bot', {}, "__main__")

tg_thread = threading.Thread(target=tg)
tg_thread.start()

def check_to_send_list():
    temp = []
    for l in main_channel_lots['to_send']:
        if main_channel_lots['to_send'][l]['start'] > datetime.now():
            with open(main_channel_lots['to_send'][l]['photo'], 'rb') as photo:
                    a = tg_bot.bot.send_photo(tg_bot.main_channel, photo,
                                            caption=main_channel_lots['to_send'][l]['cap'], 
                                            reply_markup=tg_bot.gen_keyb_card(l))
                    
                    print(f'[Log send message]: card id={l} was send at {datetime.now()}')
                    
                    temp.append(l) 
                    
                    end_time = a.caption.split('\n')[-2].split(': ')[1:][0]
                    main_channel_lots['to_delete'][a.message_id] = datetime.strptime(end_time, '%d.%m.%Y, %H:%M:%S') # timedelta can be auction default time period
    for i in temp:
        main_channel_lots['to_send'].pop(i)


def check_to_delete_list():
    temp = []
    for l in main_channel_lots['to_delete']:
        if main_channel_lots['to_delete'][l][1] < datetime.now(): 
            tg_bot.bot.delete_message(tg_bot.main_channel, l)
            if lots_bet[int(main_channel_lots['to_delete'][l][0])]['user_id']:
                usr = lots_bet[int(main_channel_lots['to_delete'][l][0])]['user_id']
                usr_name =  lots_bet[int(main_channel_lots['to_delete'][l][0])]['user_username']
                cap = main_channel_lots['to_delete'][l][2]
                lot_id = main_channel_lots['to_delete'][l][0]
                
                tg_bot.bot.send_message(usr, cap+'\n Вы выйграли аукцион. Свяжитесь с продавцом.')
                date = datetime.now()
                filepath = doc_gen.gen_default_doc(name=cap.split('\n')[0], date=date)
                with open(filepath, 'rb') as doc:
                    tg_bot.bot.send_document(usr, doc, caption="Документ")

                money = lots_bet[int(main_channel_lots['to_delete'][l][0])]['bet']
                seller = db.get_user_by_lot(int(main_channel_lots['to_delete'][l][0]))
                db.history_insert(seller[0], usr_name, lot_id, money)
                money = money * 0.05
                db.change_seller_balance(seller[0], money)
                
            temp.append(l)
            
    for i in temp:
        main_channel_lots['to_delete'].pop(i)

schedule.every(1).hours.do(check_to_send_list)
schedule.every(1).hours.do(check_to_delete_list)

while True:
    schedule.run_pending()
    time.sleep(1)   


