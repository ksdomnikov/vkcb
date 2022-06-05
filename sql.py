

import sqlite3 as sq
with sq.connect("database.db") as db:
    cur = db.cursor()
    cur.execute(""" SELECT ФИО, Имя, Телефон, vk_id FROM users WHERE vk_id = ?; """, ("122526564",))
    call = cur.fetchone()
    print(call)
t=input()