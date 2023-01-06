import argparse
import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup
from requests import HTTPError, ConnectionError

from script import get_response_from_web_library, check_for_redirect, save_book, save_image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_last_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.select("a.npage")[-1].text


def parse_book_page(soup):
    title_author_text = soup.select_one("body .ow_px_td h1").text
    title, author = title_author_text.split('::')
    genres_soup = soup.select("span.d_book a")
    genres = [genre.text for genre in genres_soup]
    comments_soup = soup.select('div.texts .black')
    comments = [comment.text for comment in comments_soup]
    relative_image_url = soup.select_one('div.bookimage img')['src']
    absolute_image_url = urljoin(f'https://tululu.org/', relative_image_url)
    book_id = soup.select_one("td.r_comm input[name='bookid'] ")['value']
    book = {
        'ID': book_id,
        'Автор': author.strip(),
        'Заголовок': title.strip(),
        'Жанр': genres,
        'Комментарии': comments,
        'Ссылка обложки': absolute_image_url
    }
    return book


def main():
    url = f"https://tululu.org/l55/"
    last_page = int(get_last_page(url)) + 1
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument(
        '-s',
        '--start_page',
        help='Укажите id начальной книги',
        nargs='?', default=1, type=int
    )
    parser.add_argument(
        '-e',
        '--end_page',
        help='Укажите id конечной книги',
        nargs='?', default=last_page, type=int
    )
    parser.add_argument(
        '-f',
        '--dest_folder',
        help='Укажите путь для скачивания',
        nargs='?', default=os.getcwd(), type=str
    )
    parser.add_argument(
        '-si',
        '--skip_image',
        help='Скачивание картинок',
        action='store_false',
        default=True
    )
    parser.add_argument(
        '-st',
        '--skip_txt',
        help='Скачивание книг',
        action='store_false',
        default=True
    )
    parser.add_argument(
        '-jp',
        '--json_path',
        help='Укажите путь JSON файла',
        nargs='?', default=os.getcwd(), type=str
    )

    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    parent_folder = args.dest_folder
    json_folder = args.json_path

    Path(parent_folder, 'image/').mkdir(parents=True, exist_ok=True)
    Path(parent_folder, 'books/').mkdir(parents=True, exist_ok=True)
    Path(json_folder).mkdir(parents=True, exist_ok=True)

    all_books = []

    books_url = []
    for page_number in range(start_page, end_page):
        page_url = f'{url}/{page_number}/'
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books = soup.select("div.bookimage a")
            for book in books:
                books_url.append(urljoin(page_url, book['href']))
        except HTTPError:
            print('HTTPError')

        except ConnectionError:
            print('ConnectionError')
            time.sleep(3)

    for book_link in books_url:
        try:
            response = requests.get(book_link)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book = parse_book_page(soup)
            book_text_response = get_response_from_web_library(book["ID"])
            check_for_redirect(book_text_response)
            filename = f'{book["ID"]}.{book["Заголовок"]}'
            image_url = book['Ссылка обложки']
            if args.skip_image:
                save_image(book["ID"], image_url, parent_folder)
            if args.skip_txt:
                save_book(book_text_response, filename, parent_folder)
            print(book_link)

            all_books.append(book)

        except HTTPError:
            print('HTTPError')

        except ConnectionError:
            print('ConnectionError')
            time.sleep(3)
    json_filepath = Path(json_folder, 'all_books_params')
    with open(json_filepath, 'w', encoding='utf8') as json_file:
        json.dump(all_books, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
