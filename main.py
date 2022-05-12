import argparse
import os
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError, ConnectionError, ReadTimeout, Timeout

BOOKDIR = 'books'
IMAGEDIR = 'images'
COMMENTSDIR = 'comments'
TIMEOUT = 5
CONNECTION_EXCEPTIONS = (ConnectionError, ReadTimeout, Timeout)


def raise_for_redirect(request_history):

    if not request_history:
        return
    if request_history[0].status_code in [301, 302]:
        raise HTTPError


def make_dirs():
    Path(BOOKDIR).mkdir(exist_ok=True, parents=True)
    Path(IMAGEDIR).mkdir(exist_ok=True, parents=True)
    Path(COMMENTSDIR).mkdir(exist_ok=True, parents=True)


def parse_bookpage_response(page_content, base_url):

    soup = BeautifulSoup(page_content, 'lxml').find(id='content')
    book_title, book_author = soup.find('h1').text.split('::')
    img_link = soup.select_one('div.bookimage img').get('src')
    book_genre = [genre_tagged.text for genre_tagged
                  in soup.select('span.d_book a')]
    comments = [comment_tagged.text for comment_tagged
                in soup.select('div.texts span')]
    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'img_url': urljoin(base_url, img_link),
        'comments': comments,
        'genre': book_genre,
    }


def download_image(img_url):

    response = requests.get(img_url, timeout=TIMEOUT)
    raise_for_redirect(response.history)
    filename = urlsplit(img_url).path.split('/')[-1]
    image_path = os.path.join(IMAGEDIR, filename)
    with open(image_path, 'wb') as file:
        file.write(response.content)


def save_comments(author, title, comments):

    comments_filepath = os.path.join(COMMENTSDIR, f'{author} - {title}.txt')
    if not comments:
        return
    with open(comments_filepath, 'wb') as file:
        for comment in comments:
            file.write(f'{comment}\n'.encode())


def download_book(author, title, book_content):

    book_title = f'{author} - {sanitize_filename(title)}.txt'
    book_filepath = os.path.join(BOOKDIR, book_title)
    with open(book_filepath, 'wb') as file:
        file.write(book_content)


def get_content(url, book_id):
    response = requests.get(url, params={'id': book_id}, timeout=TIMEOUT)
    raise_for_redirect(response.history)
    return response.content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', default=1, type=int,
                        help='С какого номера  ID начать скачивание?')
    parser.add_argument('--end_id', default=10, type=int,
                        help='Каким номером  ID закончить скачивание?')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id
    make_dirs()
    book_content_url = 'https://tululu.org/txt.php'

    book_id = start_id
    while book_id <= end_id:
        success_iteration = True
        try:
            bookpage_url = f'https://tululu.org/b{book_id}/'
            bookpage_content = get_content(bookpage_url, book_id)
            book_content = get_content(book_content_url, book_id)

            book_details = parse_bookpage_response(bookpage_content, bookpage_url)
            save_comments(book_details['author'],
                          book_details['title'],
                          book_details['comments'])
            download_book(book_details['author'],
                          book_details['title'],
                          book_content)
            download_image(book_details['img_url'])
            print(f'Скачана книга с  ID={book_id}')
        except HTTPError:
            print(f'Запрос с битым адресом: ID={book_id}')
        except CONNECTION_EXCEPTIONS:
            print('Связь с интернетом прервалась, ожидание...')
            sleep(5)
            success_iteration = False

        if success_iteration:
            book_id += 1


if __name__ == "__main__":
    main()
