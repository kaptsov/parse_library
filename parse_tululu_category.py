import argparse
import json
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, \
    ConnectionError, \
    ReadTimeout, \
    Timeout

from main import raise_for_redirect, save_comments, download_book, parse_bookpage, download_image, make_paths

CONNECTION_EXCEPTIONS = (ConnectionError, ReadTimeout, Timeout)

parser = argparse.ArgumentParser()
parser.add_argument('--start_page', default=1, type=int,
                    help='С какой страницы начать скачивание?')
parser.add_argument('--end_page', default=10, type=int,
                    help='Какой страницей закончить скачивание?')
args = parser.parse_args()

books_path = 'books'
images_path = 'images'
comments_path = 'comments'

make_paths(books_path, images_path, comments_path)

books_path = 'books'
images_path = 'images'
comments_path = 'comments'

make_paths(books_path, images_path, comments_path)


for page in range(args.start_page, args.end_page):

    url = f'https://tululu.org/l55/{page}/'
    response = requests.get(url, timeout=5)
    raise_for_redirect(response.history)
    bookpage_content = response.content
    soup = BeautifulSoup(bookpage_content, 'lxml').select_one('#content')
    book_table = soup.select('div.bookimage a')
    for book in book_table:

        print(urljoin('https://tululu.org/', book.get('href')))

        try:
            book_id = book.get('href')
            book_num = book_id[2:-1]
            bookpage_url = urljoin('https://tululu.org/', book_id)
            response = requests.get(bookpage_url, timeout=5)
            raise_for_redirect(response.history)
            bookpage_content = response.content

            book_details = parse_bookpage(bookpage_content, bookpage_url)

            with open("books.json", "a", encoding='utf8') as my_file:
                json.dump(book_details, my_file, ensure_ascii=False, indent=4)

            save_comments(book_details['author'],
                          book_details['title'],
                          book_details['comments'],
                          comments_path)
            download_book(book_details['author'],
                          book_details['title'],
                          book_num,
                          books_path)
            download_image(book_details['img_url'], images_path)
            print(f'Скачана книга с  ID={book_num}')
        except HTTPError:
            print(f'Запрос с битым адресом: ID={book_num}')
        except CONNECTION_EXCEPTIONS:
            print('Связь с интернетом прервалась, ожидание...')
            sleep(5)
            success_iteration = False


