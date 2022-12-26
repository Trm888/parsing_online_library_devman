import os
from pathlib import Path

import requests
import urllib3
from requests import HTTPError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise HTTPError('HTTP not found')


def parse_book(book_id: int):
    url = f"https://tululu.org/txt.php?id={book_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response


def save_book(book_id: int, response):
    filepath = Path(
        os.getcwd(),
        'books',
        f'Id{book_id}.txt'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)


# def main():
#     # env = Env()
#     # env.read_env()
#     Path(os.getcwd(), 'books').mkdir(parents=True, exist_ok=True)
#     book_qty = 10
#     for book_id in range(1, book_qty + 1):
#         url = f"https://tululu.org/txt.php?id={book_id}"
#         filepath = Path(
#             os.getcwd(),
#             'books',
#             f'Id{book_id}.txt'
#         )
#         response = requests.get(url)
#         try:
#             check_for_redirect(response)
#             response.raise_for_status()
#             with open(filepath, 'wb') as file:
#                 file.write(response.content)
#         except HTTPError as err:
#             print('HTTP not found')
def main():
    # env = Env()
    # env.read_env()
    Path(os.getcwd(), 'books').mkdir(parents=True, exist_ok=True)
    book_qty = 10
    for book_id in range(1, book_qty + 1):
        try:
            parsed_book = parse_book(book_id)
            if not check_for_redirect(parsed_book):
                save_book(book_id, parsed_book)

        except HTTPError:
            print('HTTP not found')


if __name__ == '__main__':
    main()
