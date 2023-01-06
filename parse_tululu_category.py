import json
import time
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup
from requests import HTTPError, ConnectionError

from script import get_response_from_web_library, check_for_redirect, save_book, save_image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_link_page(url, start_page, end_page):
    books_url = []
    for page in range(start_page, end_page + 1):
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
    print(book)
    return book


def main():
    start_page = 1
    end_page = 1
    url = f"https://tululu.org/l55/"
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
