import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def get_catalog():
    with open("all_books_params", "r", encoding="utf8") as my_file:
        films_catalog_json = my_file.read()

    films_catalog = json.loads(films_catalog_json)
    return films_catalog


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        films_catalog_column=get_catalog(),
        films_catalog_column1=get_catalog()
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
