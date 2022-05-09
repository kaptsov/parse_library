# Парсер книг с сайта tululu.org

Проект включает в себя функции для скачивания книг, обложек к ним и комментариев с сайта tululu.org.

### Как установить

Для работы требуется python3 в вашем виртуальном окружении.

```
sudo apt-get install python3.6
```

Установите необходимые библиотеки:

```
pip install -r requirements.txt
```

### Сохранение

Скачанные книги сохраняются в папках 'books', 'images', и 'comments'.


### Аргументы

Запустите скрипт командой:

```
python main.py
```


В качестве аргументов можете задать ID номер для начала выборки и конца.

--start_page - С какого номера  ID начать скачивание? По умолчанию 1.

--end_page - Каким номером  ID закончить скачивание? По умолчанию 1.


```
pyton main.py --start_page 10 --end_page 10
```

Следите за тем, чтобы начальный индекс был меньше конечного.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).