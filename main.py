import argparse
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


BOOKDIR = 'books'
IMAGEDIR = 'images'
COMMENTSDIR = 'comments'


def make_dirs():
    Path(BOOKDIR).mkdir(exist_ok=True, parents=True)
    Path(IMAGEDIR).mkdir(exist_ok=True, parents=True)
    Path(COMMENTSDIR).mkdir(exist_ok=True, parents=True)


def get_soup(book_id):

    page_url = f'https://tululu.org/b{book_id}/'
    page_content = requests.get(page_url)
    page_content.raise_for_status()
    if page_content.history:
        raise HTTPError

    return BeautifulSoup(page_content.text, 'lxml').find(id='content'), \
        page_url


def parse_book_page(soup, base_url):

    book_title, book_author = soup.find('h1').text.split('::')
    book_genre_id = soup.find('span', class_='d_book').find('a').attrs['href']
    book_genre = soup.find('span', class_='d_book').find('a').text
    img_link = soup.find('div', class_='bookimage').find('img')['src']
    comments = [comment_tagged.text for comment_tagged
                in soup.select('div.texts span')]
    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'img_url': urljoin(base_url, img_link),
        'comments': comments,
        'genre_id': book_genre_id,
        'genre': book_genre,
    }


def download_image(book_details):

    if book_details['img_url'] != 'https://tululu.org/images/nopic.gif':
        response = requests.get(book_details['img_url'])
        response.raise_for_status()
        file_type = urlsplit(book_details['img_url']).path.split('.')[-1]
        image_path = f'{IMAGEDIR}/{book_details["author"]} - ' \
            f'{book_details["title"]}.{file_type}'
        with open(image_path, 'wb') as file:
            file.write(response.content)


def download_comments(book_details):

    comment_filepath = f'{COMMENTSDIR}/{book_details["author"]} - ' \
                       f'{book_details["title"]}.txt'
    if book_details['comments']:
        with open(comment_filepath, 'wb') as file:
            for comment in book_details['comments']:
                file.write(f'{comment}\n'.encode())


def download_book(book_details, book_link):

    book_filepath = f'{BOOKDIR}/{book_details["author"]} - ' \
                    f'{book_details["title"]}.txt'
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

    for book_id in tqdm(range(start_id, end_id),
                        desc="Прогресс парсинга",
                        ncols=100,
                        bar_format='{l_bar}{bar}|'):

        try:
            book_link = requests.get(url, params={'id': book_id})
            book_link.raise_for_status()
            soup, base_url = get_soup(book_id)
            book_details = parse_book_page(soup, base_url)
            download_comments(book_details)
            download_image(book_details)
            download_book(book_details, book_link)
        except HTTPError:
            tqdm.write(f'Запрос с битым адресом. (ID={book_id})', end="")


if __name__ == "__main__":
    main()
