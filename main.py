from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from requests import HTTPError


BOOKDIR = 'books'
IMAGEDIR = 'images'
COMMENTSDIR = 'comments'


def make_dirs():
    Path(BOOKDIR).mkdir(exist_ok=True, parents=True)
    Path(IMAGEDIR).mkdir(exist_ok=True, parents=True)
    Path(COMMENTSDIR).mkdir(exist_ok=True, parents=True)


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
    book_genre_id = soup.find('span', class_='d_book').find('a').attrs['href']
    book_genre = soup.find('span', class_='d_book').find('a').text
    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'img_url': get_book_image_url(page_url, soup),
        'comments': get_comments(soup),
        'genre_id': book_genre_id,
        'genre': book_genre,
    }


def download_image(book_details):

    if book_details['img_url'] != 'https://tululu.org/images/nopic.gif':
        response = requests.get(book_details['img_url'])
        response.raise_for_status()
        file_type = urlsplit(book_details['img_url']).path.split('.')[-1]
        image_path = f'{IMAGEDIR}/{book_details["author"]} - {book_details["title"]}.{file_type}'
        with open(image_path, 'wb') as file:
            file.write(response.content)


def download_comments(comments):
    comment_filepath = f'{COMMENTSDIR}/{comments["author"]} - {comments["title"]}.txt'
    for comment in comments['comments']:
        with open(comment_filepath, 'wb') as file:
            file.write(comment)


def download_book(book_details, book_text):
    book_filepath = f'{BOOKDIR}/{book_details["author"]} - {book_details["title"]}.txt'
    with open(book_filepath, 'wb') as file:
        file.write(book_text.content)


def main():

    make_dirs()

    for book in range(10):

        url = f'https://tululu.org/txt.php?id={book}'
        page_url = f'https://tululu.org/b{book}/'

        book_text = requests.get(url)
        book_text.raise_for_status()

        if not check_for_redirect(book_text.history):
            book_data = get_book_data(page_url)
            #download_comments(book_data)
            download_image(book_data)
            download_book(book_data, book_text)


if __name__ == "__main__":
    main()