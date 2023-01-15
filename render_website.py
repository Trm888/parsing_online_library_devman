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
        films_catalog = json.load(my_file)
    return films_catalog


def on_reload(grouped_blocks_book_cards):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    blocks_qnt = len(grouped_blocks_book_cards)
    os.makedirs('pages/', exist_ok=True)
    for number, films_block in enumerate(grouped_blocks_book_cards):
        rendered_page = template.render(
            films_catalog=films_block,
            current_page=number,
            all_page=list(range(blocks_qnt)),
            last_page=blocks_qnt
        )
        filepath = Path('pages/', f'index{number}.html')
        print(filepath)
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print("Site rebuilt")


def main():
    parser = configargparse.ArgumentParser(default_config_files=['config.ini'])
    parser.add_argument('-c', '--config', is_config_file=True, help='Путь к файлу конфигурации')
    parser.add_argument('-p', '--filepath', required=True, help='Путь к файлу с фильмами')
    args = parser.parse_args()
    filepath = args.filepath
    print(filepath)
    grouped_blocks_book_cards = list(chunked(get_catalog(filepath), QUANTITY_BOOKS_ON_PAGE))

    server = Server()
    server.watch('template.html', on_reload(grouped_blocks_book_cards))

    server.serve(root='.')


if __name__ == '__main__':
    main()
