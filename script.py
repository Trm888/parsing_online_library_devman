import argparse
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError, ConnectionError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise HTTPError()


def parse_book_page(book_id: int, soup):
    title_author_tag = soup.find('td', class_="ow_px_td").find('h1')
    title_author_text = title_author_tag.text
    title, author = title_author_text.split('::')
    genres_soup = soup.find('span', class_="d_book").find_all('a')
    genres = [genre.text for genre in genres_soup]
    comments_soup = soup.find_all('div', class_="texts")
    comments = [comment.find('span').text for comment in comments_soup]
    relative_image_url = soup.find('div', class_="bookimage").find('img')['src']
    absolute_image_url = urljoin(f'https://tululu.org/b{book_id}/', relative_image_url)
    book = {
        'ID': book_id,
        'Автор': author.strip(),
        'Заголовок': title.strip(),
        'Жанр': genres,
        'Комментарии': comments,
        'Ссылка обложки': absolute_image_url
    }
    return book


def get_response_from_web_library(book_id: int):
    url = f"https://tululu.org/txt.php"
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response


def save_book(response, filename, parent_folder):
    filepath = Path(
        parent_folder,
        'books/',
        f'{sanitize_filename(filename)}.txt'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_image(book_id, image_url, parent_folder):
    response = requests.get(image_url)
    response.raise_for_status()
    url_path = urlparse(image_url).path
    extension = os.path.splitext(unquote(url_path, encoding='utf-8', errors='replace'))[1]
    filepath = Path(
        parent_folder,
        'image/',
        f'{book_id}{extension}'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)


def main():
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument(
        'start_id',
        help='Укажите id начальной книги',
        nargs='?', default=1, type=int
    )
    parser.add_argument(
        'end_id',
        help='Укажите id конечной книги',
        nargs='?', default=10, type=int
    )
    parser.add_argument(
        '-f',
        '--dest_folder',
        help='Укажите путь для скачивания',
        nargs='?', default=os.getcwd(), type=str
    )
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    parent_folder = args.dest_folder
    Path(parent_folder, 'image/').mkdir(parents=True, exist_ok=True)
    Path(parent_folder, 'books/').mkdir(parents=True, exist_ok=True)
    for book_id in range(start_id, end_id + 1):
        try:
            book_text_response = get_response_from_web_library(book_id)
            check_for_redirect(book_text_response)
            url = f'https://tululu.org/b{book_id}/'
            book_page_response = requests.get(url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
            soup = BeautifulSoup(book_page_response.text, 'lxml')
            book = parse_book_page(book_id, soup)
            print(book)
            filename = f'{book["ID"]}.{book["Заголовок"]}'
            image_url = book['Ссылка обложки']
            save_image(book_id, image_url, parent_folder)
            save_book(book_text_response, filename, parent_folder)

        except HTTPError:
            print('HTTPError')

        except ConnectionError:
            print('ConnectionError')
            time.sleep(3)


if __name__ == '__main__':
    main()
