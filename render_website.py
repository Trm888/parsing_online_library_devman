import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_catalog():
    with open("all_books_params", "r", encoding="utf8") as my_file:
        films_catalog_json = my_file.read()

    films_catalog = json.loads(films_catalog_json)
    print(films_catalog)
    return films_catalog


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    grouped_films_blocks = list(chunked(get_catalog(), 20))
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
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
