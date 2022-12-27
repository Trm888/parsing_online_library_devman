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
        raise HTTPError('HTTP not found')


def get_soup_from_book_page(book_id: int):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')

def parse_book_page(book_id: int, soup):
    title_author_tag = soup.find('td', class_="ow_px_td").find('h1')
    title_author_text = title_author_tag.text
    title, author = title_author_text.split('::')
    genres = soup.find('span', class_="d_book").find_all('a')
    genres_list = []
    for genre in genres:
        genres_list.append(genre.text)
    comments = soup.find_all('div', class_="texts")
    comment_list = []
    for comment in comments:
        comment_list.append(comment.find('span').text)
    relative_image_url = soup.find('div', class_="bookimage").find('img')['src']
    absolute_image_url = urljoin('https://tululu.org/', relative_image_url)
    book = {
        'ID': book_id,
        'Автор': author.strip(),
        'Заголовок': title.strip(),
        'Жанр': genres_list,
        'Комментарии': comment_list,
        'Ссылка обложки': absolute_image_url
    }
    return book


def get_response_from_web_library(book_id: int):
    url = f"https://tululu.org/txt.php"
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
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


def save_image(book_id, image_url, folder='image/'):
    response = requests.get(image_url)
    response.raise_for_status()
    url_path = urlparse(image_url).path
    extension = os.path.splitext(unquote(url_path, encoding='utf-8', errors='replace'))[1]
    filepath = Path(
        os.getcwd(),
        folder,
        f'{book_id}{extension}'
    )
    Path(os.getcwd(), folder).mkdir(parents=True, exist_ok=True)
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
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for book_id in range(start_id, end_id + 1):
        try:
            parsed_book = get_response_from_web_library(book_id)
            if check_for_redirect(parsed_book):
                continue
            soup = get_soup_from_book_page(book_id)
            book = parse_book_page(book_id, soup)
            print(book)
            filename = f'{book["ID"]}.{book["Заголовок"]}'
            image_url = book['Ссылка обложки']
            save_image(book_id, image_url)
            save_book(parsed_book, filename)

        except HTTPError:
            print('HTTP not found')

        except ConnectionError as err:
            print(err)
            time.sleep(3)
            continue



if __name__ == '__main__':
    main()
