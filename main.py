import argparse
import hashlib
import os
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, \
    ConnectionError, \
    ReadTimeout, \
    Timeout

CONNECTION_EXCEPTIONS = (ConnectionError, ReadTimeout, Timeout)


def raise_for_redirect(request_history):

    if request_history:
        raise HTTPError


def make_paths(books_path, images_path, comments_path):

    Path(books_path).mkdir(exist_ok=True, parents=True)
    Path(images_path).mkdir(exist_ok=True, parents=True)
    Path(comments_path).mkdir(exist_ok=True, parents=True)


def parse_bookpage(page_content, base_url):

    soup = BeautifulSoup(page_content, 'lxml').find(id='content')
    book_title, book_author = soup.find('h1').text.split('::')
    img_link = soup.select_one('div.bookimage img').get('src')
    book_genres = [genre_tagged.text for genre_tagged
                   in soup.select('span.d_book a')]
    comments = [comment_tagged.text for comment_tagged
                in soup.select('div.texts span')]
    hash = hashlib.md5(page_content).hexdigest()

    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'img_url': urljoin(base_url, img_link),
        'comments': comments,
        'genres': book_genres,
        'hash': hash
    }


def download_image(img_url, hash, path):

    response = requests.get(img_url, timeout=5)
    response.raise_for_status()
    raise_for_redirect(response.history)

    filename = urlsplit(img_url).path.split('/')[-1]
    if filename != 'nopic.gif':
        image_path = os.path.join(path, hash)

        with open(image_path, 'wb') as file:
            file.write(response.content)


def save_comments(hash, comments, path):

    comments_filename = f'comment_{hash}.txt'
    comments_filepath = os.path.join(path, comments_filename)
    if not comments:
        return
    with open(comments_filepath, 'wb') as file:
        for comment in comments:
            file.write(f'{comment}\n'.encode())


def download_book(hash, book_id, path):

    book_content_url = 'https://tululu.org/txt.php'

    response = requests.get(book_content_url,
                            params={'id': book_id},
                            timeout=5)
    response.raise_for_status()
    raise_for_redirect(response.history)

    book_content = response.content

    book_title = f'book_{hash}.txt'
    book_filepath = os.path.join(path, book_title)
    with open(book_filepath, 'wb') as file:
        file.write(book_content)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', default=1, type=int,
                        help='С какого номера  ID начать скачивание?')
    parser.add_argument('--end_id', default=10, type=int,
                        help='Каким номером  ID закончить скачивание?')
    args = parser.parse_args()

    books_path = 'books'
    images_path = 'images'
    comments_path = 'comments'

    make_paths(books_path, images_path, comments_path)

    book_id = args.start_id
    end_id = args.end_id

    while book_id <= end_id:
        success_iteration = True
        try:
            bookpage_url = f'https://tululu.org/b{book_id}/'
            response = requests.get(bookpage_url, timeout=5)
            raise_for_redirect(response.history)
            bookpage_content = response.content

            book_details = parse_bookpage(bookpage_content, bookpage_url)
            save_comments(book_details['hash'],
                          book_id,
                          comments_path)
            download_book(book_details['hash'],
                          book_id,
                          books_path)
            download_image(book_details['img_url'],
                           book_details['hash'],
                           images_path)
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
