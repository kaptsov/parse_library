import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from tqdm import tqdm

BOOKDIR = 'books'
IMAGEDIR = 'images'
COMMENTSDIR = 'comments'


def raise_for_redirect(request_history):

    if request_history:
        raise HTTPError


def make_dirs():
    Path(BOOKDIR).mkdir(exist_ok=True, parents=True)
    Path(IMAGEDIR).mkdir(exist_ok=True, parents=True)
    Path(COMMENTSDIR).mkdir(exist_ok=True, parents=True)


def get_page_content(book_id):

    page_url = f'https://tululu.org/b{book_id}/'
    page_content = requests.get(page_url)
    page_content.raise_for_status()
    raise_for_redirect(page_content.history)

    return page_url, page_content


def parse_book_page(page_content, base_url):

    soup = BeautifulSoup(page_content.text, 'lxml').find(id='content')
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

    response = requests.get(img_url)
    response.raise_for_status()
    raise_for_redirect(response.history)
    filename = urlsplit(img_url).path.split('/')[-1]
    image_path = os.path.join(IMAGEDIR, f'{filename}')
    with open(image_path, 'wb') as file:
        file.write(response.content)


def save_comments(author, title, comments):

    comments_filepath = os.path.join(COMMENTSDIR, f'{author} - {title}.txt')
    if comments:
        with open(comments_filepath, 'wb') as file:
            for comment in comments:
                file.write(f'{comment}\n'.encode())


def download_book(author, title, book_link):

    book_filepath = os.path.join(BOOKDIR, f'{author} - {title}.txt')
    with open(book_filepath, 'wb') as file:
        file.write(book_link.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', default=1, type=int,
                        help='С какого номера  ID начать скачивание?')
    parser.add_argument('--end_id', default=10, type=int,
                        help='Каким номером  ID закончить скачивание?')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id + 1
    make_dirs()
    url = 'https://tululu.org/txt.php'
    loop_range = tqdm(range(start_id, end_id),
                      desc="Прогресс парсинга",
                      ncols=100,
                      bar_format='{l_bar}{bar}|')

    for book_id in loop_range:

        try:
            book_link = requests.get(url, params={'id': book_id})
            book_link.raise_for_status()
            raise_for_redirect(book_link.history)
            base_url, page_content = get_page_content(book_id)
            book_details = parse_book_page(page_content, base_url)
            save_comments(book_details['author'],
                          book_details['title'],
                          book_details['comments'])
            download_book(book_details['author'],
                          book_details['title'],
                          book_link)
            download_image(book_details['img_url'])
        except HTTPError:
            tqdm.write(f'Запрос с битым адресом. (ID={book_id})', end="")


if __name__ == "__main__":
    main()
