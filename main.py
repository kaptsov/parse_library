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


def get_book_image_url(url, soup):
    return urljoin(url, soup.find('div', class_='bookimage').find('img')['src'])


def get_comments(soup):
    comments = []
    raw_comments = soup.find_all('div', class_='texts')
    for raw_comment in raw_comments:
        comments.append(raw_comment.find('span').text)
    return comments

def get_book_data(page_url):
    page_content = requests.get(page_url)
    page_content.raise_for_status()
    soup = BeautifulSoup(page_content.text, 'lxml').find(id='content')
    book_title, book_author = soup.find('h1').text.split('::')
    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'img_url': get_book_image_url(page_url, soup),
        'comments': get_comments(soup)
    }


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
            book_data = get_book_data(page_url)
            book_title = book_data['title']
            book_author = book_data['author']
            book_image_url = book_data['img_url']
            comments = book_data['comments']
            print(comments)
            download_image(book_image_url, book_title, book_author)
            filename = f'{BOOKDIR}/{book_author} - {book_title}.txt'
            with open(filename, 'wb') as file:
                file.write(book_text.content)


if __name__ == "__main__":
    main()