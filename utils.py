import logging

from bs4 import BeautifulSoup, Tag
from requests import RequestException, Response

from exceptions import ParserFindTagException


def get_response(session, url) -> Response | None:
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True,
        )


def find_tag(soup: BeautifulSoup | Tag, tag: str, attrs=None) -> Tag:
    searched_tag: Tag | None = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
