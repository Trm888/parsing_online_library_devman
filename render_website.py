import json
import os
from pathlib import Path

import configargparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

QUANTITY_BOOKS_ON_PAGE = 20


def get_catalog(filepath):
    with open(filepath, "r", encoding="utf8") as my_file:
        books_catalog = json.load(my_file)
    return books_catalog


def on_reload():
    parser = configargparse.ArgumentParser(default_config_files=['config.ini'])
    parser.add_argument('-c', '--config', is_config_file=True, help='Путь к файлу конфигурации')
    parser.add_argument('-p', '--filepath', required=True, help='Путь к файлу с информацией о книгах')
    args = parser.parse_args()
    filepath = args.filepath
    grouped_blocks_book_cards = list(chunked(get_catalog(filepath), QUANTITY_BOOKS_ON_PAGE))
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    blocks_quantity = len(grouped_blocks_book_cards)
    os.makedirs('pages/', exist_ok=True)
    for number, block_book_cards in enumerate(grouped_blocks_book_cards):
        rendered_page = template.render(
            books_catalog=block_book_cards,
            current_page=number,
            all_page=list(range(blocks_quantity)),
            last_page=blocks_quantity
        )
        filepath = Path('pages/', f'index{number}.html')
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
