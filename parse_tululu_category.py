import argparse
import json
import time
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


def parse_link_page(url, start_page, end_page):
    books_url = []
    for page in range(start_page, end_page):
        url_page = f'{url}/{page}/'
        response = requests.get(url_page)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.select("div.bookimage a")
        for book in books:
            books_url.append(urljoin(url_page, book['href']))
    return books_url


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
    # print(book)
    return book


def main():
    url = f"https://tululu.org/l55/"
    last_page = int(get_last_page(url)) + 1
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument(
        'start_page',
        help='Укажите id начальной книги',
        nargs='?', default=1, type=int
    )
    parser.add_argument(
        'end_page',
        help='Укажите id конечной книги',
        nargs='?', default=last_page, type=int
    )
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page

    book_links = parse_link_page(url, start_page, end_page)
    all_books = []
    for book_link in book_links:
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
            save_image(book["ID"], image_url)
            save_book(book_text_response, filename)
            print(book_link)

            all_books.append(book)

        except HTTPError:
            print('HTTPError')

        except ConnectionError:
            print('ConnectionError')
            time.sleep(3)

    with open('all_books_params', 'w', encoding='utf8') as json_file:
        json.dump(all_books, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
