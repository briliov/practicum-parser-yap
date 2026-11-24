from bs4 import BeautifulSoup
import requests

LOGIN_URL = 'http://130.193.59.87/login/'


data = {
    'username': 'test_parser_user',
    'password': 'testpassword',
}


session = requests.session()

response = session.get(LOGIN_URL)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'lxml')
token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

data['csrfmiddlewaretoken'] = token

response = session.post(LOGIN_URL, data=data)
response.encoding = 'utf-8'
print(response.status_code)
