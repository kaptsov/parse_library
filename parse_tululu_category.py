import argparse
import json
import os.path
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', default=1, type=int,
                        help='С какой страницы начать скачивание?')
    parser.add_argument('--end_page', default=10, type=int,
                        help='Какой страницей закончить скачивание?')
    parser.add_argument('--dest_folder', default='',
                        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument('--json_path', default='books.json',
                        help='Название JSON файла для сохранения данных книг')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать книги')
    args = parser.parse_args()

    books_path = os.path.join(args.dest_folder, 'books')
    images_path = os.path.join(args.dest_folder, 'images')
    comments_path = os.path.join(args.dest_folder, 'comments')

    make_paths(books_path, images_path, comments_path)

    for page in range(args.start_page, args.end_page):

        url = f'https://tululu.org/l55/{page}/'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        raise_for_redirect(response.history)

        bookpage_content = response.content
        soup = BeautifulSoup(bookpage_content, 'lxml').select_one('#content')
        tags_on_page = soup.select('div.bookimage a')
        for book_tag in tags_on_page:

            print(urljoin('https://tululu.org/', book_tag.get('href')))

            try:
                book_id = book_tag.get('href')
                book_num = book_id[2:-1]
                bookpage_url = urljoin('https://tululu.org/', book_id)
                response = requests.get(bookpage_url, timeout=5)
                response.raise_for_status()
                raise_for_redirect(response.history)

                bookpage_content = response.content
                book_details = parse_bookpage(bookpage_content, bookpage_url)

                with open(os.path.join(args.dest_folder, args.json_path), "a", encoding='utf8') as json_file:
                    json.dump(book_details, json_file, ensure_ascii=False, indent=4)

                save_comments(book_details['author'],
                              book_details['title'],
                              book_details['comments'],
                              comments_path)
                if not args.skip_txt:
                    download_book(book_details['author'],
                                  book_details['title'],
                                  book_num,
                                  books_path)
                if not args.skip_imgs:
                    download_image(book_details['img_url'], images_path)
                print(f'Скачана книга с  ID={book_num}')
            except HTTPError:
                print(f'Запрос с битым адресом: ID={book_num}')
            except CONNECTION_EXCEPTIONS:
                print('Связь с интернетом прервалась, ожидание...')
                sleep(5)


if __name__ == '__main__':
    main()
