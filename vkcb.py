# Импорт нужных библиотек
import sqlite3
import colorama
from colorama import Fore, Back, Style
import vk_api
from vk_api import VkUpload
from vk_api import keyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
colorama.init()

# Сообщение в консоль о запуске чат-бота
print(Fore.CYAN + "     \n  Запуск чат-бота... OK") 

ofert = "C:/Users/Kirill/Desktop/cb/dogovor-oferta.pdf"  # ВОТ СЮДА НУЖНО УКАЗАТЬ ПОЛНЫЙ ПУТЬ К ДОКУМЕНТУ
pricelist = ""

# Вставляем токен от нашего сообщества для получения ботом доступа
token = "88f6dd734ce666b65f187e898d772e7b91d11a19bbed42efd499f0f33dfb48f884438b51b1b41300780c3" # СОЮДА НУЖНО ВСТАВИТЬ ТОКЕН В КАВЫЧКАХ
authorise = vk_api.VkApi(token = token)
longpoll = VkLongPoll(authorise)
upload = VkUpload(authorise)


# Определяем функцию отправки сообщения с параметрами (vk_id отправителя, отправляемое сообщение, отправка клавиетуры)
def write_message(sender, message, keyboard=None, attachment=None):  
    post = {                                        
        "user_id": sender,
        "message": message,
        "random_id": get_random_id()
    }
    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()
    if attachment != None:
        post["attachment"] = attachments[attachment]
    else:
        pass
    authorise.method('messages.send', post)
   

# Создаем SQL базу данных, если ее нет, с соответствующими столбцами
with sqlite3.connect("database.db") as db:
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        ФИО TEXT,
        Имя TEXT,
        Телефон TEXT,
        vk_id INTEGER,
        menu INTEGER,
        Ожидается_оплата INTEGER DEFAULT 0,
        Ссылка_для_оплаты TEXT,
        Код TEXT,
        Отзыв TEXT 
        )""")

# Сообщение в консоль о подключении базы данных
print(Fore.CYAN + "     \n  Подключение базы данных... OK")

# Ждем сообщения от пользователя и составляем сценарий
for event in longpoll.listen(): 
    # Ждем сообщение от пользователя и записываем в пременные сообщение и его vk_id
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        recieved_message = event.text.lower()
        sender = event.user_id
        attachments = []
        upload_doc = upload.document_message(doc = ofert, peer_id = sender, title = 'Договор оферта')['doc']
        attachments.append('doc{}_{}'.format(upload_doc['owner_id'], upload_doc['id']))
        # Считываем из базы данных пункт меню присвоенный текущему пользователю
        '''
        Параметр menu b и интерпретация принимаемых значений
        None - пользователь не взаимодействовал с чат-ботом
        0 - пользователь отправил первое сообщение чат-боту и его vk_id записан в базу данных
        1 - договор оферта
        2 - пользователь перешел по регистрации и должен ввести имя
        3 - пользователь вводит фамилию 
        4 - польователь ввел имя и должен ввести номер телефона(НУЖНО РЕАЛИЗОВАТЬ ПОДТВЕРЖДЕНИЕ)
        5 - пользователь прошел регистрацию и находится в главном меню
        6 - пользователь захотел оставить отзыв/пожелания/предложения
        БУДЕТ ДОПОЛНЯТЬСЯ
        '''
        with sqlite3.connect("database.db") as db: # Смотрим в базе зарегистрирован ли пользователь
            cur = db.cursor()
            cur.execute(""" SELECT menu FROM users WHERE vk_id = ?""", (event.user_id,))
            
        try:
            menu = cur.fetchone()[0]
            
            if menu == 4:
                with sqlite3.connect("database.db") as db: # Смотрим есть ли ссылка для оплаты
                    cur = db.cursor()
                    cur.execute(""" SELECT Ссылка_для_оплаты FROM users WHERE vk_id = ?""", (event.user_id,))


                if recieved_message == "главное меню" or recieved_message == "все понятно, в главное меню" :
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Как постирать вещи?", color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button("Изменить данные", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button("Пожелания/предложения", color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button("Заказать звонок", color=VkKeyboardColor.SECONDARY)
                    keyboard.add_line()
                    keyboard.add_button("Проблема", color=VkKeyboardColor.NEGATIVE)
                    write_message(sender, ".", keyboard)
                
                elif recieved_message == "как постирать вещи?": 
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Все понятно, в главное меню", color=VkKeyboardColor.PRIMARY)
                    write_message(sender, "ИНСТРУКЦИЯ КАК СТИРАТЬ ВМЕСТЕ ОБСУДИМ И НАПИШЕМ: Предварительно оставляет вещи в постамате по номеру телефона-> мы присылаем ему ссылку на оплату(она пришлется автоматически из базы данных через чат бота) либо тетки будут писать ее через вконтакте вручную так еще проще -> факт оплаты и код получения мы вносим в таблицу ->  человеку присылаетс также код в сообщении", keyboard)
                
                elif recieved_message == "начать": 
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Изменить данные", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "Вы уже записаны у меня в базе, Вы можете изменить свои данные или перейти в главное меню", keyboard)

                elif recieved_message == "проблема": 
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" SELECT ФИО, Имя, Телефон, vk_id FROM users WHERE vk_id = ?; """, (sender,))
                        call = cur.fetchone()
                        print("\n" + Back.RED + Fore.WHITE + "  У клиента проблема, нужно ему позвонить.\n  Данные - | ФИО:", call[0], "| Имя:", call[1], "| Телефон:", call[2], "| vk_id:", call[3])
                    write_message(sender, "Мы скоро с Вами свяжемся, чтобы решить проблему.  Если что-то срочное, то можете позвонить по номеру:")
                    write_message(sender, "<НОМЕР ДЛЯ СВЯЗИ НАПИШЕМ>", keyboard)
                
                elif recieved_message == "заказать звонок": 
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" SELECT ФИО, Имя, Телефон, vk_id FROM users WHERE vk_id = ?; """, (sender,))
                        call = cur.fetchone()
                        print("\n" + Back.CYAN + Fore.BLACK + "  Клиент заказал звонок.\n  Данные - | ФИО:", call[0], "| Имя:", call[1], "| Телефон:", call[2], "| vk_id:", call[3])
                    write_message(sender, "Спасибо за обращение! Мы скоро с Вами свяжемся.", keyboard)
                
                elif recieved_message == "изменить данные":
                    write_message(sender, "Отлично, давайте Вас запишем!")
                    write_message(sender, "Напишите свои имя и фамилию через пробел, так я буду к Вам обращаться.")
                    write_message(sender, "Например: Иван Кузнецов")
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" UPDATE users SET menu = ? WHERE vk_id = ?; """, (2,sender))
                
                elif recieved_message == "пожелания/предложения" or recieved_message == "пожелания" or recieved_message == "предложения" or recieved_message == "отзыв":
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" UPDATE users SET menu = ? WHERE vk_id = ?; """, (5,sender))
                    write_message(sender, "Напишите, что в нашем сервисе Вам кажется можно сделать лучше.\nЕсли Ваше предложение улучшит наш сервис, то мы подарим бонусы, которыми Вы сможете оплатить стирку")
                
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                    write_message(sender, "Я не смог распознать Ваш запрос, но со временем я научусь понимать, что от меня хотят, а пока используйте пожалуйста кнопки меню, чтобы избежать ошибок в моей работе.", keyboard)

            elif menu == 0:
    
                if recieved_message == "о нас":
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Регистрация", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "ТУТ БУДЕТ КРАТКАЯ ИНФОРМАЦИЯ О НАШЕМ СЕРВИСЕ И ЦЕНЫ НА УСЛУГИ, МОЖНО ОФОРМИТЬ В ВИДЕ КАРТИНКИ С ТЕКСТОМ И ОТПРАВИТЬ ЕЁ")
                    write_message(sender, "А теперь давайте перейдем к регистрации.", keyboard)

                elif recieved_message == "регистрация":
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Принять", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "Перед регистрацией нужно ознакомиться и принять договор оферту", keyboard, attachment=0)

                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" UPDATE users SET menu = ? WHERE vk_id = ?; """, (1,sender))
                    
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("О нас", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Регистрация", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "Чтобы я смог выполнять основные запросы необходимо пройти небольшую регистрацию.", keyboard)

            elif menu == 1:
                if recieved_message == "принять":
                    write_message(sender, "Отлично, давайте Вас запишем!")
                    write_message(sender, "Напишите свои имя и фамилию через пробел, так я буду к Вам обращаться.")
                    write_message(sender, "Например: Иван Кузнецов")
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" UPDATE users SET menu = ? WHERE vk_id = ?; """, (2,sender))
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Принять", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "Чтобы пройти регистрацию, нужно ознакомиться и принять договор оферту. Без этого, по закону, мы не сможем принимать у Вас заказы", keyboard)

            elif menu == 2:
                if len(recieved_message) != 0:
                        name = event.text.lower().split()
                        write_message(sender, "Приятно познакомиться, " + name[0].capitalize() + "!" )
                        write_message(sender, "Теперь напишите свой номер с восьмеркой, чтобы я смог принимать у Вас заказы. \n Пример: 89121234567 (11 цифр)")
                        with sqlite3.connect("database.db") as db:
                            cur = db.cursor()
                            cur.execute(""" UPDATE users SET (menu, ФИО) = (?, ?) WHERE vk_id = ?; """, (3, name[1].capitalize() + ' ' + name[0].capitalize(),sender))
                else:
                    
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("О нас", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Регистрация", color=VkKeyboardColor.POSITIVE)
                    write_message(sender, "Чтобы я смог выполнять основные запросы нужно пройти небольшую регистрацию.", keyboard)

            elif menu == 3:
                if len(recieved_message) != 0:
                    tel = recieved_message
                    if len(tel) == 11 and recieved_message.isdigit():
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button("Как постирать вещи?", color=VkKeyboardColor.POSITIVE)
                        keyboard.add_line()
                        keyboard.add_button("Изменить данные", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button("Пожелания/предложения", color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button("Заказать звонок", color=VkKeyboardColor.SECONDARY)
                        keyboard.add_line()
                        keyboard.add_button("Проблема", color=VkKeyboardColor.NEGATIVE)
                        with sqlite3.connect("database.db") as db:
                            cur = db.cursor()
                            cur.execute(""" UPDATE users SET (menu, Телефон) = (?, ?) WHERE vk_id = ?; """, (4, recieved_message, sender))
                        write_message(sender, "Отлично, Ваш номер: " + tel + " я тоже записал.\n Спасибо за регистрацию!",keyboard )
                    else:
                        write_message(sender, "В номере вышла ошибка, я не могу его прочитать, попробуйте пожалуйста написать еще раз, как в примере")
                
            elif menu == 5:
                if len(recieved_message) != 0:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                    with sqlite3.connect("database.db") as db:
                        cur = db.cursor()
                        cur.execute(""" UPDATE users SET menu = ?, Отзыв = ? WHERE vk_id = ?; """, (4, recieved_message, sender))
                    write_message(sender, "Спасибо за помощь в улучшении нашей работы, мы обязательно все прочитаем!", keyboard)

        except:
            if len(recieved_message) != 0: 
                with sqlite3.connect("database.db") as db:
                    cur = db.cursor()
                    cur.execute(""" SELECT vk_id FROM users WHERE vk_id = ?""", (sender,))
                    if cur.fetchone() == None:
                        cur.execute(""" INSERT INTO users(vk_id, menu) VALUES (?, ?); """, (sender,0))
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button("О нас", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_button("Регистрация", color=VkKeyboardColor.POSITIVE)
                        write_message(sender, "Привет, мы сервис аквачистки Фреш!\nМы можем рассказать о себе или сразу перейдем к небольшой регистрации?", keyboard )
                    else:
                        keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY)
                        write_message(sender, "Привет, мы сервис аквачистки Фреш!\nМы уже знаем Вас, можем перейти сразу в главное меню", keyboard)
                        cur.execute(""" UPDATE users(vk_id, menu) VALUES (?, ?); """, (sender,3))