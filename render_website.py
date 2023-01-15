import argparse
import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_catalog(filepath):
    with open(filepath, "r", encoding="utf8") as my_file:
        films_catalog_json = my_file.read()

    films_catalog = json.loads(films_catalog_json)
    print(films_catalog)
    return films_catalog


def on_reload(grouped_films_blocks):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')


    blocks_qnt = len(grouped_films_blocks)
    os.makedirs('pages/', exist_ok=True)
    for number, films_block in enumerate(grouped_films_blocks):
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
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument('-p', '--filepath', help='Укажите путь к файлу', default='all_books_params')
    args = parser.parse_args()
    filepath = args.filepath
    grouped_films_blocks = list(chunked(get_catalog(filepath), 20))

    # on_reload(grouped_films_blocks)
    server = Server()
    server.watch('template.html', on_reload(grouped_films_blocks))

    server.serve(root='.')


if __name__ == '__main__':
    main()
