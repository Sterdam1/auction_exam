import sched
import threading
import runpy
import time
import sys
from datetime import datetime, timedelta
import tg_bot


scheduler = sched.scheduler(time.time, time.sleep)

def delete_messag(chat_id, message_id, end_time):
        try:
            print(f'[Log scheduler]: auction message {message_id} is over. ({end_time})')

        except Exception as e:
            print("Ошибка при удалении сообщения:", e)

    
def add_lot(lot, chat_id):
    message_id, end_time = lot
    scheduler.enterabs(end_time.timestamp(), 1, delete_messag, (chat_id, message_id, end_time.strftime("%m.%d.%Y, %H:%M:%S")))
    print(scheduler.queue)


def scheduler_worker():
    scheduler.run()

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=scheduler_worker)
    delay = timedelta(seconds=5)  # Указываем через сколько удалить сообщение (10 секунд в данном случае)
    end_time = datetime.now() + delay

    add_lot([12313212,end_time], 123)
    scheduler_thread.start()
    
    add_lot([12313212,datetime.now() + timedelta(seconds=10)], 321)