import os
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise HTTPError('HTTP not found')


def parse_book_page(book_id: int):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
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
    book_information = {
        'ID': book_id,
        'Автор': author.strip(),
        'Заголовок': title.strip(),
        'Жанр': genres_list,
        'Комментарии': comment_list,
        'Ссылка обложки': absolute_image_url
    }
    return book_information


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
    Path(os.getcwd(), 'books').mkdir(parents=True, exist_ok=True)
    book_qty = 10
    for book_id in range(1, book_qty + 1):
        try:
            parsed_book = parse_book(book_id)
            if not check_for_redirect(parsed_book):
                book_information = parse_book_page(book_id)
                print(book_information)
                filename = f'{book_information["ID"]}.{book_information["Заголовок"]}'
                image_url = book_information['Ссылка обложки']
                save_image(book_id, image_url)
                save_book(parsed_book, filename)

        except HTTPError:
            print('HTTP not found')


if __name__ == '__main__':
    main()
