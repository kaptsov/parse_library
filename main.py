import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests
from requests import HTTPError

DIR = 'books'


def make_dirs():
    try:
        os.makedirs(DIR)
    except FileExistsError:
        # directory already exists
        pass


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
            filename = f'{DIR}/{book_author} - {book_title}.txt'
            with open(filename, 'wb') as file:
                file.write(book_text.content)


if __name__ == "__main__":
    main()