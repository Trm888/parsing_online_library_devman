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

    block_films = list(chunked(get_catalog(), 20))

    os.makedirs('pages/', exist_ok=True)
    for number, page in enumerate(block_films):

        rendered_page = template.render(
            films_catalog=page
        )
        filepath = Path('pages/', f'index{number}.html')
        print(filepath)
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print("Site rebuilt")


def main():
    # server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    # server.serve_forever()
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
