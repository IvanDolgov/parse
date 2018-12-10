!!! НЕ АКТУАЛЕН, так как на сайте obrazkras.ru перестали публиковать информацию о зачислении

Телеграм бот для парсинга новостей сайта obrazkras.ru
Зачем это нужно? Быть готовым к тому что появится путевка в сад и не протетерить день выдачи путевок.

1) Создаете бота. Очень много статей в интернете , как создать бота
Нам нуже токен.

2) Предварительная настройка
требуется Python2.7
Требуется mysql


pip install pymysql
pip install telebot
pip install lxml

3) Далее создаем папку с нашим проектом
git clone git://github.com/IvanDolgov/parse /root/parseobrazgit

4) Создаем базу. дамп obrazkras.sql
создаем базу данных obrazkras
импорт sql
моздаем пользователя и пароль

Ее в sql загнать. Советую прогнать в sql строку . Чтобы начать парсить хотя бы с 1630 (это с 2018 года)
INSERT INTO `parsenews` (`page`) VALUES ('1630'); 

5) Убираем индексирование с конфига
git update-index --assume-unchanged config.py
вносим изменения в config.py
- данные о базе
- токен бота
- ИД админа

6) Запуск
cd /root/parseobrazgit
Запускаем:
python2.7 parse.py 

рекомендую supervisor для того чтобы бот всегда был запущен


---
Ищем и обавляем бота себе. 
можно начинать первый парсинг командой в боте "Погрузить новые данные с сайта".

После нескольких прогонов у Вас наберется база свитдетельств за 2018 год. (мне хватило 5-ти прогонов)

----------------------------
Чтобы не тыркать постоянно на кнопку проверки новых данных. советую cronparse.py загнать в крон (один-два раза в сутки и по будням)

-------------------

Ну а далее работайте с ботом.
