import logging
import re
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup, Tag
from requests import Response
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session: requests_cache.CachedSession) -> list[tuple]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response: Response | None = get_response(session, whats_new_url)
    if response is None:
        raise Exception('Не удалось получить ответ от сервера')
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    main_div: Tag = find_tag(
        soup,
        'section',
        attrs={'id': 'what-s-new-in-python'},
    )
    div_with_ul: Tag = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper'},
    )
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'},
    )

    results: list[tuple] = [
        ('Ссылка на статью', 'Заголовок', 'Редактор, автор'),
    ]
    for section in tqdm(sections_by_python):
        version_a_tag: Tag = find_tag(section, 'a')
        if not version_a_tag.has_attr('href'):
            raise Exception('Тег a не содержит атрибут href')
        if not isinstance(href := version_a_tag.get('href'), str):
            raise Exception('Ссылка на статью не найдена')
        version_link = urljoin(whats_new_url, href)
        response: Response | None = get_response(session, version_link)
        if response is None:
            continue
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1: Tag = find_tag(soup, 'h1')
        dl: Tag = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text),
        )
    return results


def latest_versions(session: requests_cache.CachedSession) -> list[tuple]:
    response: Response | None = get_response(session, MAIN_DOC_URL)
    if response is None:
        raise Exception('Не удалось получить ответ от сервера')
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar: Tag = find_tag(
        soup,
        'div',
        attrs={'class': 'sphinxsidebarwrapper'},
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')

    results: list[tuple] = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        if not a_tag.has_attr('href'):
            raise Exception('Тег a не содержит атрибут href')
        if not isinstance(link := a_tag.get('href'), str):
            raise Exception('Ссылка на документацию не найдена')
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            status, version = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session: requests_cache.CachedSession):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    downloads_dir: Path = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)

    response: Response | None = get_response(session, downloads_url)
    if response is None:
        raise Exception('Не удалось получить ответ от сервера')
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    main_div: Tag = find_tag(soup, 'div', attrs={'role': 'main'})
    if main_div:
        table: Tag = find_tag(main_div, 'table', attrs={'class': 'docutils'})
        pdf_a4_tag = find_tag(
            table,
            'a',
            {'href': re.compile(r'.+html\.zip$')},
        )
        pdf_a4_link = pdf_a4_tag.get('href', '')
        if not isinstance(pdf_a4_link, str):
            raise Exception('Ссылка на архив не найдена')
        archive_url = urljoin(downloads_url, pdf_a4_link)
        filename = archive_url.split('/')[-1]
        archive_path: Path = downloads_dir / filename
        response = session.get(archive_url)
        with open(archive_path, 'wb') as file:
            file.write(response.content)
        logging.info(
            f'Архив был загружен и сохранен: {archive_path}',
        )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results: list[tuple] = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу')


if __name__ == '__main__':
    main()
