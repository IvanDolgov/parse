# -*- coding: utf-8 -*-
import config
import urllib2
import time
import lxml.html.clean
import lxml.html
import pymysql
from datetime import datetime

db = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_password, db=config.mysql_db, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True, autocommit=True)
cur0 = db.cursor(pymysql.cursors.DictCursor)
sql0 = 'SELECT MAX(page) FROM parsenews'
cur0.execute(sql0)
p = cur0.fetchone()
max = p['MAX(page)']
k=0
for page in range(int(max)+1, int(max)+30):
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
cur0.close()
#добавть в таблицу, чтоб потом можно было узнавать сколько в день добавило св-тв
#print("Парсинг закончен. Добавлено "+str(k)+" новых записей")
cur2 = db.cursor(pymysql.cursors.DictCursor)
sql2 = """INSERT INTO `parseevent` (`amount`,`eventtime`) VALUES (%s,%s)"""
eventtime = datetime.now()
cur2.execute(sql2, (k,eventtime))
db.commit()
cur2.close()
db.close
