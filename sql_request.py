import sqlite3 as sl
db = sl.connect('auction/db.sqlite3', check_same_thread=False)

main_channel_lots = {'to_send':{},
                     'to_delete': {}}

lots_bet = {}

ready_lots = []

class DataBase:
    def __init__(self):
        global db
        self.db = db

    def history_insert(self, seller_id, buyer, lot_id, price, sell_date):
        with self.db as con:
            con.execute(f"""INSERT INTO lotlist_sellhistory (buyer, price, created_by_id, lot_id, sell_date)
                        VALUES ('{buyer}', '{price}', '{seller_id}', '{lot_id}', '{sell_date}')""")

    def insert_report(self, user_reported, who_reported, cause):
        with self.db as con:
            con.execute(f"""INSERT INTO lotlist_report (reported_username, user_that_reported, cause) 
                        VALUES ('{user_reported}', '{who_reported}', '{cause}')""")


    def get_user_by_lot(self, lot_id):
        with self.db as con:
            user = con.execute(f"""SELECT created_by_id, seller_link FROM lotlist_lot WHERE id = {lot_id}""").fetchone()
            
        return user

    def change_seller_balance(self, user_id, sel):
        with self.db as con:
            balance = con.execute(f"""SELECT balance FROM lotlist_userfinance finance
                                    WHERE user_id = {user_id}""").fetchone()
            users = con.execute(f"""UPDATE lotlist_userfinance 
                                SET balance = {balance[0]-sel}
                                WHERE id = {user_id};""")

    def change_lot_status(self, lot_id):
        with self.db as con:
            con.execute(f"""UPDATE lotlist_lot
                            SET ready_status_id = 2
                            WHERE id = {lot_id}""")
            

    def get_ready_lots(self):
        with self.db as con:
            ready_lots = con.execute("""SELECT lot.id, lot.lot_name, lot.start_price, lot.seller_link, lot.lot_geo, lot.lot_description, lot.start_time, lot.end_time 
                                    FROM lotlist_lot lot
                                    WHERE lot.ready_status_id = 1;""").fetchall()
            lot_img = con.execute("""SELECT lot_image.lot_id AS lot_id, image.img AS image_name
                                    FROM lotlist_lot_img lot_image
                                    JOIN lotlist_image image ON lot_image.image_id = image.id;""").fetchall()
        return ready_lots, lot_img
    

#    dont use  
    # def droppo(self, table):
    #     with self.db as con:
    #         con.execute(f"""DROP TABLE {table}""")

    def cretete(self, table):
        with self.db as con:
            con.execute(f"""CREATE TABLE""")
db = DataBase()
