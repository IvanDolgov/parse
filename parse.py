# -*- coding: utf-8 -*-
import config
import urllib2
import time
import lxml.html.clean
import lxml.html
import pymysql
import telebot
from telebot import types
from datetime import datetime,timedelta
from telebot import apihelper

bot = telebot.TeleBot(config.token)
apihelper.proxy = {  'https': 'socks5://{}:{}@{}:{}'.format(config.user_s,config.pass_s,config.ip_s,config.port_s)}

#не понял зачем, но команды не принимает бот без нее. Проблемы с юникодом
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@bot.message_handler(commands=['start'])
def start(message):
    checkusersdb(message)
    bot.send_message(message.chat.id,"Привет - я бот. Ищу информацию на сайте obrazkras. Но не доверяйте мне слепо - проверйяте меня.")


def start_menu(message):
    time.sleep(1)
    if message.chat.id == config.adminid:
        keyboard = types.ReplyKeyboardMarkup(True, False)
        button_check = types.KeyboardButton(text="Проверить мое свидетельство")
        button_masscheck = types.KeyboardButton(text="Проверить св-ва всех Юзеров")
        button_parse = types.KeyboardButton(text="Подгрузить новые данные с сайта")
        last_parse = types.KeyboardButton(text="Последние загрузки")
        button_showdoc = types.KeyboardButton(text="Показать мои св-ва")
        #button_changenumber = types.KeyboardButton(text="Ввести данные св-ва о рождении")
        keyboard.row(button_check)
        keyboard.row(button_masscheck)
        keyboard.row(button_parse)
        keyboard.row(last_parse)
        keyboard.row(button_showdoc)
        #keyboard.row(button_changenumber)
        bot.send_message(message.chat.id, 'Выберите пункт меню: ', reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(True,False)
        button_geo = types.KeyboardButton(text="Проверить мое свидетельство")
        button_showdoc = types.KeyboardButton(text="Показать мои св-ва")
        #button_changenumber = types.KeyboardButton(text="Ввести данные св-ва о рождении")
        keyboard.row(button_geo)
        keyboard.row(button_showdoc)
        #keyboard.row(button_changenumber)
        bot.send_message(message.chat.id, 'Выберите пункт меню: ', reply_markup=keyboard)


#проверка есть ли юзер в базе
def checkusersdb(message):
    db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT tid,firstname,lastname,username FROM users WHERE tid="+str(message.chat.id)
    cur.execute(sql)
    result=cur.fetchone()
    if result is None:
        addusersdb(message)
        zaprosnumber(message)
    else:
        bot.send_message(message.chat.id,'Привет, %s %s' % (result['firstname'], result['lastname']))
        start_menu(message)
    cur.close()
    db.close()


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.reply_to_message is not None)
def addnumber(message):
    sernumber=message.text
    sernumber=sernumber.replace('"','')
    sernumber = sernumber.replace('№', '')
    t=sernumber.split()
    ser=t[0]
    numb=t[1]
    db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql1= """INSERT INTO `documents` (`tid`,`ser`,`numb` ) VALUES (%s,%s,%s)"""
    cur.execute(sql1, (message.chat.id, ser, numb))
    cur.close()
    db.close()
    showmedocuments(message)


def addusersdb(message):
    regtime = datetime.now()
    db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql1 = """INSERT INTO `users` (`tid`,`firstname`,`lastname`,`username`,`regtime` ) VALUES (%s,%s,%s,%s,%s)"""
    cur.execute(sql1,(message.chat.id, message.chat.first_name, message.chat.last_name, message.chat.username, regtime))
    result = cur.fetchone()
    db.commit()
    bot.send_message(message.chat.id, 'Привет, %s  %s' % (result['firstname'], result['lastname']))
    bot.send_message(config.adminid,  'Новый пользователь %s %s ' % (result['firstname'],result['lastname']))
    cur.close()
    db.close()
    return


@bot.message_handler(func=lambda message: message.text == 'Проверить мое свидетельство' and message.content_type == 'text')
def checknumber(message):
    db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True)
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT tid,ser,numb FROM documents WHERE tid=" + str(message.chat.id)
    cur.execute(sql)
    for row in cur:
        try:
            cur1 = db.cursor(pymysql.cursors.DictCursor)
            sql1 = "SELECT id_page,ser,numb,datex,page FROM parsenews WHERE numb=" + str(row['numb'])
            cur1.execute(sql1)
            for row1 in cur1:
                if cur1 is not None:
                    bot.send_message(message.chat.id,'Возможно нашел информацию с такими цифрами...')
                    bot.send_message(message.chat.id,'Серия %s Номер %s' %(row1['ser'],row1['numb']))
                    bot.send_message(message.chat.id,'Внимательно прочитайте новость http://obrazkras.ru/news/' + str(row1['page']) + '/')

            else:
                bot.send_message(message.chat.id, 'Нет данных о св-ве ' + str(row['ser'])+' № '+str(row['numb']))
            cur1.close()
        except IndexError:
            bot.send_message(message.chat.id, 'Я незнаю номера свидетельства Вашего ребенка')
            zaprosnumber(message)
    start_menu(message)
    cur.close()
    db.close()

@bot.message_handler(func=lambda message: message.text == 'Показать мои св-ва' and message.content_type == 'text')
def showmedocuments(message):
    db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT tid,ser,numb FROM documents WHERE tid=" + str(message.chat.id)
    cur.execute(sql)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for row in cur:
        button = types.InlineKeyboardButton(text=row['ser'] + " № " + row['numb'],callback_data="test"+row['ser']+row['numb'])
        button2= types.InlineKeyboardButton(text="Х", callback_data="clear_one "+row['ser']+" "+row['numb'])
        keyboard.add(button,button2)
    button_changenumber = types.InlineKeyboardButton(text="Ввести данные св-ва о рождении",callback_data="add_document")
    button_clear = types.InlineKeyboardButton(text="Очистить список", callback_data="clear_list")
    button_back = types.InlineKeyboardButton(text="Назад в главное", callback_data="back")
    keyboard.add(button_changenumber)
    keyboard.add(button_clear)
    keyboard.add(button_back)
    bot.send_message(message.chat.id, "Ваши св-ва", reply_markup=keyboard)
    cur.close()
    db.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        # Очистка списка всех свидеельств
        if call.data == "clear_list":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Все св-ва удалены")
            db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
            cur = db.cursor(pymysql.cursors.DictCursor)
            sql= "DELETE FROM documents WHERE tid=" + str(call.message.chat.id)
            try:
                cur.execute(sql)
            except NameError:
                print('error')
            db.commit()
            cur.close()
            db.close()
            showmedocuments(call.message)
        #удаление выбранного свидетельства
        if "clear_one" in call.data:
            element=call.data.split(' ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Свидетельство удалено")
            db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password,db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8',
                                 use_unicode=True, autocommit=True)
            cur = db.cursor(pymysql.cursors.DictCursor)
            sql = "DELETE FROM documents WHERE ser='" + str(element[1])+"' and numb='"+str(element[2]+"'")
            try:
                cur.execute(sql)
            except NameError:
                print('error')
            db.commit()
            cur.close()
            db.close()
            showmedocuments(call.message)
        # добавление свидетельства
        if "add_document" in call.data:
            zaprosnumber(call.message)
        if "back" in call.data:
            start_menu(call.message)
        if "test" in call.data:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Функцонала нет еще")



@bot.message_handler(func=lambda message: message.text == 'Ввести данные св-ва о рождении' and message.content_type == 'text')
def zaprosnumber(message):
    keyboard0 = types.ForceReply(selective=True)
    bot.send_message(message.chat.id, 'Введите серию и номер св-ва о рождении. Пример "VI-13 112345"', reply_markup=keyboard0)


# Админская!!!запускать или админом. и добавить "добавлять только новые страницы"
@bot.message_handler(func=lambda message: message.text == 'Подгрузить новые данные с сайта' and message.content_type == 'text')
def parsenew(message):
    if message.chat.id == config.adminid:
        db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
        cur0 = db.cursor(pymysql.cursors.DictCursor)
        sql0 = 'SELECT MAX(page) FROM parsenews'
        cur0.execute(sql0)
        p = cur0.fetchone()
        max = p['MAX(page)']
        k=0
        for page in range(int(max)+1, int(max)+20):
            time.sleep(3)
            url = 'http://obrazkras.ru/news/' + str(page) + '/'
            html_content = urllib2.urlopen(url).read()
            html_code = lxml.html.clean.clean_html(html_content)
            root = lxml.html.fromstring(html_code)
            k1=0
            for tbl in root.xpath('.//div[@class="news-detail"]//table'):
                elements = tbl.xpath('.//tr//td//text()')
                try:
                    k2 = 0
                    for i in range(0, 100):
                        cur = db.cursor(pymysql.cursors.DictCursor)
                        data_table = (elements[0 + 4 * i].encode('raw-unicode-escape').replace('\r\n\t\t\t ', '').replace('\r\n\t\t',''),
                                           elements[1 + 4 * i].encode('raw-unicode-escape').replace('\r\n\t\t\t ', '').replace('\r\n\t\t',''),
                                           elements[2 + 4 * i].encode('raw-unicode-escape').replace('\r\n\t\t\t ', '').replace('\r\n\t\t',''),
                                           elements[3 + 4 * i].encode('raw-unicode-escape').replace('\r\n\t\t\t ', '').replace('\r\n\t\t',''),
                                           page)
                        sql1 = """INSERT INTO `parsenews` (`id_page`,`ser`,`numb`,`datex`,`page` ) VALUES (%s,%s,%s,%s,%s)"""
                        cur.execute(sql1, data_table)
                        k2=k2+1
                        cur.close()
                except IndexError:
                    print('error')
                k1=k1+k2
            k=k+k1
        db.commit()

        bot.send_message(message.chat.id, "Парсинг закончен. Добавлено "+str(k)+" новых записей")
        cur0.close()

        cur2 = db.cursor(pymysql.cursors.DictCursor)
        sql2 = """INSERT INTO `parseevent` (`amount`,`eventtime`) VALUES (%s,%s)"""
        eventtime = datetime.now()
        cur2.execute(sql2, (k, eventtime))
        db.commit()
        cur2.close()

        db.close()

@bot.message_handler(func=lambda message: message.text == 'Последние загрузки' and message.content_type == 'text')
def last_parse(message):
    if message.chat.id == config.adminid:
        a = datetime.now()
        b=timedelta(days=3)
        c=a-b
        db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True)
        cur = db.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT id,amount,eventtime FROM parseevent WHERE eventtime > '"+ str(c)+"'"
        cur.execute(sql)
        bot.send_message(message.chat.id, "Загрузки за последние 3 дня:")
        for row in cur:
            bot.send_message(message.chat.id, str(row['amount'])+" шт. "+str(row['eventtime'])+" ")
        cur.close()
        db.close()

#запускать по расписанию каждое утро и оповещать счастливчиков
@bot.message_handler(func=lambda message: message.text == 'Проверить св-ва всех Юзеров' and message.content_type == 'text')
def mass_check(message):
    if message.chat.id == config.adminid:
        db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True)
        cur = db.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT tid,ser,numb FROM documents"
        cur.execute(sql)
        k = 0
        for row in cur:
            cur1 = db.cursor(pymysql.cursors.DictCursor)
            sql1 = "SELECT id_page,ser,numb,datex,page FROM parsenews WHERE numb=" + str(row['numb'])
            cur1.execute(sql1)
            k1 = 0
            for row1 in cur1:
                if cur1 is not None:
                    bot.send_message(row['tid'], 'Возможно нашел информацию с такими цифрами...')
                    bot.send_message(row['tid'], 'Серия %s Номер %s' % (row1['ser'], row1['numb']))
                    bot.send_message(row['tid'], 'Внимательно прочитайте новость http://obrazkras.ru/news/' + str(row1['page']) + '/')
                k1 = k1+1
            k = k + k1
            cur1.close
        bot.send_message(config.adminid, 'Найдено ' + str(k) + ' соответствий')
        cur.close()
        db.close()

if __name__ == '__main__':
    bot.polling(none_stop=True)
