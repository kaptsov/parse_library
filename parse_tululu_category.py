from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import main


for page in range(1, 5):

    url = f'https://tululu.org/l55/{page}/'
    response = requests.get(url, timeout=5)
    main.raise_for_redirect(response.history)
    bookpage_content = response.content
    soup = BeautifulSoup(bookpage_content, 'lxml').find(id='content')
    book_table = soup.find_all('table')
    for book in book_table:
        print(urljoin('https://tululu.org/', book.find('a').attrs['href']))


