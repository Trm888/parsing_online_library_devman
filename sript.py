import os
from pathlib import Path

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
import urllib3
from requests import HTTPError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise HTTPError('HTTP not found')


def parse_name(book_id: int):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_author_tag = soup.find('body').find('td', class_="ow_px_td").find('h1')
    title_author_text = title_author_tag.text
    title, author = title_author_text.split('::')
    return f'{book_id}.{title.strip()}'

def parse_book(book_id: int):
    url = f"https://tululu.org/txt.php?id={book_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response


def save_book(response, filename, folder='books/'):
    filepath = Path(
        os.getcwd(),
        folder,
        f'{sanitize_filename(filename)}.txt'
    )
    Path(os.getcwd(), folder).mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(response.content)




def main():
    # env = Env()
    # env.read_env()
    Path(os.getcwd(), 'books').mkdir(parents=True, exist_ok=True)
    book_qty = 10
    for book_id in range(1, book_qty + 1):
        try:
            parsed_book = parse_book(book_id)
            if not check_for_redirect(parsed_book):
                filename = parse_name(book_id)
                save_book(parsed_book, filename)

        except HTTPError:
            print('HTTP not found')


if __name__ == '__main__':
    main()
