import os
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_books(book_qty: int):
    for book_id in range(1, book_qty + 1):
        url = f"https://tululu.org/txt.php?id={book_id}"
        filepath = Path(
            os.getcwd(),
            'books',
            f'Id{book_id}.txt'
        )

        response = requests.get(url)
        response.raise_for_status()
        with open(filepath, 'wb') as file:
            file.write(response.content)


def main():
    # env = Env()
    # env.read_env()
    Path(os.getcwd(), 'books').mkdir(parents=True, exist_ok=True)
    download_books(10)


if __name__ == '__main__':
    main()
