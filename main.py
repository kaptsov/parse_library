import os
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


def get_book_name(url):
    page_content = requests.get(url).text
    soup = BeautifulSoup(page_content, 'lxml').find(id='content')
    book_title, book_author = soup.find('h1').text.split('::')
    return book_title.strip(), book_author.strip()


def main():

    make_dirs()

    for book in range(10):

        url = f'https://tululu.org/txt.php?id={book}'
        page_url = f'https://tululu.org/b{book}/'

        response = requests.get(url)
        response.raise_for_status()

        if not check_for_redirect(response.history):
            book_title, book_author = get_book_name(page_url)
            filename = f'{DIR}/{book_author} - {book_title}.txt'
            with open(filename, 'wb') as file:
                file.write(response.content)


if __name__ == "__main__":
    main()