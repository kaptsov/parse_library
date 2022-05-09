import requests
import os

DIR = 'books'

try:
    os.makedirs(DIR)
except FileExistsError:
    # directory already exists
    pass


for book in range(10):

    url = f'https://tululu.org/txt.php?id=321{book}'

    response = requests.get(url)
    response.raise_for_status()

    filename = f'{DIR}/text{book}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)