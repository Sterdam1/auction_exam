from datetime import datetime, timedelta

import telebot
import sys
from sql_request import main_channel_lots, lots_bet, ready_lots
from sql_request import db
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '6417186164:AAFKXtgvEToBCuiNyTQ_hloO3fxDIkNUa2s'
bot = telebot.TeleBot(TOKEN)

main_channel = '@exam_auction'
support_chat_id = -4036488176

template = ["Название: ", "\nСтартовая цена: ", "\nПродавец: @", "\nАдрес лота: ", "\nОписание: ", "\nНачало аукциона: ", "\nОкончание аукциона: "]

keyb_close = InlineKeyboardMarkup()
keyb_close.add(InlineKeyboardButton('Закрыть', callback_data='close-close'))

sessions = {}
cash = {'to_close': []}

photos = {}
captions = {}

def gen_keyb_card(lot_id):
        # user card keyboard: open lot button, that redirect user straight to the bot. 
        # P.S. May be needs smth to change or add
        keyb_card_user = InlineKeyboardMarkup()
        keyb_card_user.add(InlineKeyboardButton('Открыть лот', url=f"https://t.me/Auction0987654321bot?start={lot_id}"))
        return keyb_card_user


if __name__ == '__main__':

    

    def gen_captions(lots):
            # gen captions: gen card captions to send in future
            cards = {}

            for lot in lots[0]:
                card = ''
                for t in range(len(template)):
                    if t == 5:
                        if lot[t+1] != None:
                            time = datetime.strptime(lot[t+1], '%Y-%m-%d %H:%M:%S')
                            time = time.strftime('%d.%m.%Y, %H:%M:%S')
                            card += template[t] + time
                        else:
                            card += template[t] + 'сразу после публикации' 
                    elif t == 6:
                        if lot[t+1] != None:
                            time = datetime.strptime(lot[t+1], '%Y-%m-%d %H:%M:%S')
                            time = time.strftime('%d.%m.%Y, %H:%M:%S')
                            card += template[t] + time
                        else: 
                            card += template[t] + 'Через 1 день'  
                    else:
                        card += template[t] + str(lot[t+1])

                cards[lot[0]] = card

            return cards

    def gen_photos(lots):
        # Gen photos: gen photo paths to open in future 
        photo_dict = {}

        for photo in lots[1]:
            if photo[0] in photo_dict:
                photo_dict[photo[0]].append(f'auction/media/{photo[1]}')
                continue
            photo_dict[photo[0]] = [f'auction/media/{photo[1]}']

        return photo_dict

    def send_in_time(photo, caption, lot_id, end_time):
        with open(photo, 'rb') as photo_file:
                    a = bot.send_photo(main_channel, photo_file, caption=caption, reply_markup=gen_keyb_card(lot_id))
                    main_channel_lots['to_delete'][a.message_id] = [lot_id, end_time, caption]
        return a
    
        
    def gen_keyb_card_sup(lot_id):
        # support card keyboard: approve, decline and download buttons
        keyb_card = InlineKeyboardMarkup()
        keyb_card.add(InlineKeyboardButton('Подтвердить', callback_data=f'apr-{lot_id}'), InlineKeyboardButton('Отказать', callback_data=f'decl-{lot_id}')) # apr = approve, decl = decline
        keyb_card.add(InlineKeyboardButton('Скачать файлы', callback_data=f'dl-{lot_id}')) #dl = download 
        
        return keyb_card

    def gen_keyb_card_user(lot_id):
        keyb_card = InlineKeyboardMarkup()
        keyb_card.add(InlineKeyboardButton('Сделать ставку', callback_data=f'bet-{lot_id}'))
        keyb_card.add(InlineKeyboardButton('Настроить ставку', callback_data=f'hbet-{lot_id}'))
        keyb_card.add(InlineKeyboardButton('Скачать файлы', callback_data=f'dl-{lot_id}'))

        return keyb_card

    def gen_keyb_bet(lot_id):
        keyb_bet = InlineKeyboardMarkup()
        keyb_bet.add(InlineKeyboardButton('10', callback_data=f'b-1-{lot_id}'), 
                    InlineKeyboardButton('50', callback_data=f'b-2-{lot_id}'), InlineKeyboardButton('100', callback_data=f'b-3-{lot_id}'))
        keyb_bet.add(InlineKeyboardButton('Сбросить ставку', callback_data=f'cancel-{lot_id}'),
                    InlineKeyboardButton('Сохранить скрытую ставку', callback_data=f'close-save-{lot_id}'))

        return keyb_bet

    @bot.message_handler(content_types=['text'])
    def start(message):
        global photos, captions, main_channel_lots, ready_lots
        if message.text.startswith('/start') and message.chat.id != support_chat_id:
            lot_id = int(message.text.split(' ')[1])
            bot.delete_message(message.chat.id, message.message_id)
            
            if message.chat.id not in sessions:
                sessions[message.chat.id] = {'balance': 500,
                                            'lots': {}}
                cap = captions[lot_id] + '\n' + 'Ваша ставка: 0'
            else: 
                cap = captions[lot_id] + '\n' + f"Ваша ставка: {sessions[message.chat.id]['lots'][lot_id]}"
        
            with open(photos[lot_id][0], 'rb') as photo:
                bot.send_photo(message.chat.id, photo, cap, reply_markup=gen_keyb_card_user(lot_id))

        elif message.text == '/balance' and message.chat.id != support_chat_id:
            if message.chat.id not in sessions:
                sessions[message.chat.id] = {'balance': 500,
                                            'lots': {}}
            bot.send_message(message.chat.id, f'Ваш баланс: {sessions[message.chat.id]["balance"]}', reply_markup=keyb_close)
            cash['to_close'].append(message.message_id)
                
        elif message.text == '/report' and message.chat.id != support_chat_id:
            if message.chat.id not in sessions:
                sessions[message.chat.id] = {'balance': 500,
                                            'lots': {}}
            bot.send_message(message.chat.id, 'Напишите ник продавца или админа на которого хотите пожаловаться напишите !cancel чтобы выйти',)
            bot.register_next_step_handler(message, report1)
        # update command: deletes all messages and send ready lots to approve or decline; 
        elif message.text == '/update' and message.chat.id == support_chat_id:
            if 'lots' in cash:
                if cash['lots']:
                    for lots in cash['lots']:
                        bot.delete_message(chat_id=message.chat.id, message_id=lots)
                    cash['lots'] = []
            
            bot.delete_message(message.chat.id, message.id)
            
            ready_lots = db.get_ready_lots()
            photos = gen_photos(ready_lots)
            captions = gen_captions(ready_lots)

            for cap in captions:
                with open(photos[cap][0], 'rb') as photo:
                    lot_card_id = bot.send_photo(message.chat.id, photo, captions[cap], reply_markup=gen_keyb_card_sup(cap))
                if 'lots' in cash:
                    cash['lots'].append(lot_card_id.message_id)
                    continue
                cash['lots'] = [lot_card_id.message_id]

    def report1(message):
        if message.text == '!cancel':
            return
        bot.send_message(message.chat.id, 'Введите причину')           
        bot.register_next_step_handler(message, report2, message.text)

    def report2(message, nick):
        if message.text == '!cancel':
            return
        db.insert_report(nick, message.from_user.username, message.text)
        bot.send_message(message.chat.id, 'Ваша жалоба отпралена.') 

    @bot.callback_query_handler(func=lambda call: True)
    def query_handler(call):
        global main_channel_lots

        bot.answer_callback_query(callback_query_id=call.id)
        print(f'[Log call.data]: {call.data}.')
        sys.stdout.flush()
        
        # download callback: send a message with extra files 
        if call.data.split('-')[0] == 'dl':
            photos = gen_photos(ready_lots)
            photo_files = photos[int(call.data.split('-')[1])] # call.data.split('-')[1] = card id 
            media_group = [telebot.types.InputMediaPhoto(open(photo, 'rb'), ) for photo in photo_files[1:]]
            if media_group:
                media = bot.send_media_group(call.message.chat.id, media_group)
            else:
                media = [bot.send_message(call.message.chat.id, 'Нет дополнительных файлов.')]
            bot.send_message(call.message.chat.id, 'Понятно', reply_markup=keyb_close)
            
            if 'to_close' in cash:
                for m in media:
                    cash['to_close'].append(m.message_id)
                cash['to_close'].append(close.message_id)
            else:
                cash['to_close'] = [close.message_id]
                for m in media:
                    cash['to_close'].append(m.message_id)
        
        # close callback: delete messages with extra file for comfortability
        elif call.data.split('-')[0] == 'close' and call.data.split('-')[1] == 'close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if 'to_close' in cash:
                for close in cash['to_close']:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=close)
                cash['to_close'] = []

        # approve callback: approves lot and send it to main channel
        elif call.data.split('-')[0] == 'apr':
            photos = gen_photos(ready_lots)
            photo = photos[int(call.data.split('-')[1])][0]
            start_time = datetime.now()
            end_time = datetime.now() + timedelta(minutes=5)  # timedelta can be auction default time period

            if call.message.caption.split(': ')[-1] != 'Через 1 день':
                    end_time = datetime.strptime(call.message.caption.split(': ')[-1], '%d.%m.%Y, %H:%M:%S')
            
            if call.message.caption.split(': ')[-2].startswith('сразу после публикации'):

                cap = '\n'.join(call.message.caption.split('\n')[:-2]) + \
                    f'\nАункцион начался: {start_time.strftime("%d.%m.%Y, %H:%M:%S")}'+ \
                    f'\nАукнцион закончиться: {end_time.strftime("%d.%m.%Y, %H:%M:%S")}'
                a = send_in_time(photo=photo, caption=cap, lot_id=call.data.split('-')[1], end_time=end_time)
                main_channel_lots['to_delete'][a.message_id] = [call.data.split('-')[1], end_time, cap]
            else:
                start_time = call.message.caption.split(': ')[-2].split('\n')[0]
                cap = '\n'.join(call.message.caption.split('\n'))[:-2] + \
                    f'\nАункцион начался в {start_time}'+ \
                    f'\nАукнцион закончиться: {end_time.strftime("%d.%m.%Y, %H:%M:%S")}'
                
                main_channel_lots['to_send'][int(call.data.split('-')[1])] = {'start': datetime.strptime(start_time, '%d.%m.%Y, %H:%M:%S'),
                                                                              'cap': cap,
                                                                              'photo': photo}
            
            captions[int(call.data.split('-')[1])] = cap

            lots_bet[int(call.data.split('-')[1])] = {'bet': 0,
                                                 'user_id': None,
                                                 'user_username': ''}
               
            bot.delete_message(call.message.chat.id, call.message.message_id)

            cash['lots'].remove(call.message.message_id)


        # decline callback: decline lot and delete message. 
        # P.S. may be need to change or add smth
        elif call.data.split('-')[0] == 'decl':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if 'lots' in cash:
                if call.message.message_id in cash['lots']:
                    cash['lots'].remove(call.message.message_id)
        
        elif call.data.split('-')[0] == 'bet':
            lot_id = call.data.split('-')[1]
            if lot_id in sessions[call.message.chat.id]['lots']:
                if sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] != 0:
                    sessions[call.message.chat.id]['lots'][lot_id]['bet'] += sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] 
                    # sessions[call.message.chat.id]['balance'] -= sessions[call.message.chat.id]['lots'][lot_id]['bet']
                    # sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] = 0

                    if sessions[call.message.chat.id]['lots'][lot_id]['bet'] > sessions[call.message.chat.id]['lots'][lot_id]['s_price']:
                        if lots_bet[int(lot_id)]['bet'] < sessions[call.message.chat.id]['lots'][lot_id]['bet']:
                            if lots_bet[int(lot_id)]['user_id']:
                                if call.message.chat.id != lots_bet[int(lot_id)]['user_id']:
                                    bot.send_message(lots_bet[int(lot_id)]['user_id'], 'Вашу ставку перебили!', reply_markup=keyb_close )    
                                
                            lots_bet[int(lot_id)] = {'bet': sessions[call.message.chat.id]['lots'][lot_id]['bet'],
                                                    'user_id': call.message.chat.id,
                                                    'user_username': call.from_user.username}
                                                
                            for s in sessions:
                                if s != call.message.chat.id:
                                    sessions[s]['balance'] += sessions[s]['lots'][lot_id]['bet']
                                    sessions[s]['lots'][lot_id]['bet'] = 0

                            for lot in main_channel_lots['to_delete']:
                                if main_channel_lots['to_delete'][lot][0] == lot_id:
                                    bot.edit_message_caption(chat_id=main_channel, message_id=lot, 
                                        caption=main_channel_lots['to_delete'][lot][2]+ \
                                        f'\nСамая высокая ставка: {lots_bet[int(lot_id)]["bet"]} {lots_bet[int(lot_id)]["user_username"]}',
                                        reply_markup=gen_keyb_card(lot_id))
                                    break
                            
                            sessions[call.message.chat.id]['balance'] -= sessions[call.message.chat.id]['lots'][lot_id]['bet']
                            # sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] = 0

                            cap = ': '.join(call.message.caption.split(': ')[:-1]) + \
                                f": {str(sessions[call.message.chat.id]['lots'][lot_id]['bet'])}"

                            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                    caption=cap,
                                                    reply_markup=gen_keyb_card_user(lot_id))
                        else:
                            bot.send_message(call.message.chat.id, 'Ставка слишком мала чтоб перебить предыдущую.', reply_markup=keyb_close)
                            sessions[call.message.chat.id]['lots'][lot_id]['bet'] = 0
                            print(f'[Log bet]: ваша ставка {lots_bet[int(lot_id)]["bet"]} < чем прошлая')
                    else:
                        sessions[call.message.chat.id]['lots'][lot_id]['bet'] = 0
                        bot.send_message(call.message.chat.id, 'Ставка меньше чем стартовая цена.', reply_markup=keyb_close)

        elif call.data.split('-')[0] == 'hbet':
            lot_id = call.data.split('-')[1]
            start_price = call.message.caption.split('\n')[1].split(': ')[1]
            if lot_id not in sessions[call.message.chat.id]['lots']:
                sessions[call.message.chat.id]['lots'][lot_id] = {'bet': 0, 'hid_bet': 0, 's_price': float(start_price)}
                bet = sessions[call.message.chat.id]['lots'][lot_id]['hid_bet']
            else: 
                bet = sessions[call.message.chat.id]['lots'][lot_id]['hid_bet']
            bot.send_message(call.message.chat.id, 
                            f'Изменяйте скрытую ставку \nВаша ставка: {bet}', 
                            reply_markup=gen_keyb_bet(lot_id))
        
        elif call.data.split('-')[0] == 'b':
            lot_id = call.data.split('-')[2]
            temp_list = [10, 50, 100] # DSMTH
            for i in range(len(temp_list)):
                if int(call.data.split('-')[1]) == i+1:
                    sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] += temp_list[i]  
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f"Изменяйте скрытую ставку \nВаши ставка: " +
                                        str(sessions[call.message.chat.id]['lots'][lot_id]['hid_bet']),
                                        reply_markup=gen_keyb_bet(lot_id))
                    
                    print(f'[Log sessions]: {sessions}.')
                    sys.stdout.flush()
                    break

        elif call.data.split('-')[0] == 'cancel':
            lot_id = call.data.split('-')[1]
            if sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] != 0:
                sessions[call.message.chat.id]['lots'][lot_id]['hid_bet'] = 0
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f"Изменяйте скрытую ставку \nВаши ставка: 0",
                                    reply_markup=gen_keyb_bet(lot_id))
                
            print(f'[Log sessions]: Hidden bet of lot_id={lot_id} was returned to 0.')
            sys.stdout.flush()

        elif call.data.split('-')[1] == 'save' and call.data.split('-')[0] == 'close':
            lot_id = call.data.split('-')[2]
            bot.delete_message(call.message.chat.id, call.message.message_id)

            print(f'[Log sessions]: Hidden bet of lot_id={lot_id} was saved' +
                f'({sessions[call.message.chat.id]["lots"][lot_id]["hid_bet"]}).')
            sys.stdout.flush()
    
    

    bot.infinity_polling(timeout=10)