import os
from urllib.parse import urljoin, urlsplit
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests import HTTPError


BOOKDIR = 'books'
IMAGEDIR = 'images'


def make_dirs():
    Path(BOOKDIR).mkdir(exist_ok=True, parents=True)
    Path(IMAGEDIR).mkdir(exist_ok=True, parents=True)


def check_for_redirect(history):
    try:
        return history
    except HTTPError:
        pass


def get_book_image(url, page_content):
    soup = BeautifulSoup(page_content.text, 'lxml').find(id='content')
    image_url = urljoin(url, soup.find('div', class_='bookimage').find('img')['src'])
    return  image_url


def get_book_name(page_content):
    soup = BeautifulSoup(page_content.text, 'lxml').find(id='content')
    book_title, book_author = soup.find('h1').text.split('::')
    return book_title.strip(), book_author.strip()


def download_image(url, book_title, book_author):

    if url != 'https://tululu.org/images/nopic.gif':
        response = requests.get(url)
        response.raise_for_status()
        file_type = urlsplit(url).path.split('.')[-1]
        filename = f'{IMAGEDIR}/{book_author} - {book_title}.{file_type}'
        with open(filename, 'wb') as file:
            file.write(response.content)


def main():

    make_dirs()

    for book in range(10):

        url = f'https://tululu.org/txt.php?id={book}'
        page_url = f'https://tululu.org/b{book}/'

        book_text = requests.get(url)
        book_text.raise_for_status()
        page_response = requests.get(page_url)
        page_response.raise_for_status()

        if not check_for_redirect(book_text.history):
            book_title, book_author = get_book_name(page_response)
            print(get_book_image(page_url, page_response))
            download_image(get_book_image(page_url, page_response), book_title, book_author)
            filename = f'{BOOKDIR}/{book_author} - {book_title}.txt'
            with open(filename, 'wb') as file:
                file.write(book_text.content)


if __name__ == "__main__":
    main()