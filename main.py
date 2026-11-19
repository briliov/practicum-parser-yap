import logging
import re
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output


def whats_new(session: requests_cache.CachedSession) -> list[tuple]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = session.get(whats_new_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = soup.find('section', attrs={'id': 'what-s-new-in-python'})
    if main_div is None:
        raise Exception('Не найден блок с id what-s-new-in-python')
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    if div_with_ul is None:
        raise Exception('Не найден блок с классом toctree-wrapper')
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'},
    )

    results: list[tuple] = [
        ('Ссылка на статью', 'Заголовок', 'Редактор, автор'),
    ]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        if version_a_tag is None:
            raise Exception('Не найден тег a в секции')
        if not version_a_tag.has_attr('href'):
            raise Exception('Тег a не содержит атрибут href')
        version_link = urljoin(whats_new_url, version_a_tag.get('href', ''))
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = soup.find('h1')
        dl = soup.find('dl')
        if dl is None:
            raise Exception(f'Не найден тег dl на странице {version_link}')
        dl_text = dl.text.replace('\n', ' ')
        if h1 is None:
            raise Exception(f'Не найден тег h1 на странице {version_link}')
        results.append(
            (version_link, h1.text, dl_text),
        )
    return results


def latest_versions(session: requests_cache.CachedSession) -> list[tuple]:
    response = session.get(MAIN_DOC_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = soup.find('div', attrs={'class': 'sphinxsidebarwrapper'})
    if not sidebar:
        raise Exception('Не найден блок с классом sphinxsidebarwrapper')
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
        link = a_tag.get('href', '')
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

    response = session.get(downloads_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = soup.find('div', {'role': 'main'})
    if main_div:
        table_tag = main_div.find('table', {'class': 'docutils'})
        if table_tag:
            pdf_a4_tag = table_tag.find(
                'a',
                {'href': re.compile(r'.+html\.zip$')},
            )
            if pdf_a4_tag:
                pdf_a4_link = pdf_a4_tag.get('href', '')
                if isinstance(pdf_a4_link, str):
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
