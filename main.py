import requests
import os

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


def main():

    make_dirs()
    for book in range(10):

        url = f'https://tululu.org/txt.php?id=321{book}'

        response = requests.get(url)
        response.raise_for_status()

        if not check_for_redirect(response.history):
            filename = f'{DIR}/text{book}.txt'
            with open(filename, 'wb') as file:
                file.write(response.content)


if __name__ == "__main__":
    main()