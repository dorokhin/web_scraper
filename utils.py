from useragent import random_user_agent
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import datetime
from lxml import etree, html
from pathlib import Path
import urllib.request
import uuid
import gzip
import os


env_path = Path(__file__).resolve().parent / 'secret.env'
print(load_dotenv(dotenv_path=env_path, verbose=True))
# Check if secret.env loaded successfully
# otherwise raise KeyError
if os.environ['ENV_LOAD_SUCCESS']:
    pass


def create_directory(local_path):
    local_path = Path(local_path)
    local_path.mkdir(parents=True, exist_ok=True)


def download_file(params, headers=None):
    req = urllib.request.Request(
        params['original_url'],
        data=None,
        headers=headers if headers else {
                'User-Agent': random_user_agent(),
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    )

    create_directory(params['local_file_path'])
    full_path = params['local_file_path'] + params['new_filename']
    with urllib.request.urlopen(req) as response, open(full_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)


def get_file_params(url):
    parsed_url = urlparse(url)
    base_media_path = os.environ['BASE_MEDIA_PATH']
    media_url = os.environ['MEDIA_URL']
    path_by_extension = {
        'jpg': '/images/',
        'jpeg': '/images/',
        'gif': '/images/',
        'png': '/images/',
        'css': '/css/',
        'default': '/other/',
    }
    today = datetime.today()
    file_extension = url.split('.')[-1]
    local_file_path = path_by_extension[file_extension]
    local_file_path = base_media_path + local_file_path + f'{today.year}/{today.month}/'
    original_filename = os.path.basename(parsed_url.path)
    new_filename = f'{str(uuid.uuid4())}.{file_extension}'
    return {
        'original_url': url,
        'original_filename': original_filename,
        'new_filename': new_filename,
        'local_file_path': local_file_path,
        'web_path': media_url,
        'full_url': media_url + '/' + new_filename,
    }


def create_job_download_file(params):
    """
    This doesn't work, currently stub
    :param params:
    :return:
    """
    print('Creating download schedule for file:', params['original_url'])


def fix_links(content):
    """
    Функция находит в переданном фрагменте html, ссылки на внешние ресурсы,
    в случае файлов - загружает их на локальный сервер, попутно заменяя ссылку на новую.

    Находим параметр src либо href, для href производим коррекцию (замену) доменного имени на наш.
    Для src: сначала загружаем файл, предварительно определив его тип и выбрав соответствующую директорию на сервере, в
    зависимости от типа (mime-type: img [jpg, png, gif, etc...], css, other type).

    Путь сохранения генерируем в функции get_file_path(existing_url),
    затем загружаем файл,
    после заменяем путь в тексте

    :param content:
    :return: html с изменёнными ссылками на ресурсы
    """
    content = content.strip()
    tree = html.fragment_fromstring(content, create_parent=True)

    for node in tree.xpath('//*[@src]'):
        url = node.get('src')
        file_params = get_file_params(url)
        create_job_download_file(file_params)
        url = file_params['full_url']
        node.set('src', url)

    data = etree.tostring(tree, pretty_print=False, encoding="utf-8")

    return data


def get_html(url, headers=None):
    req = urllib.request.Request(
        url,
        data=None,
        headers=headers if headers else {
                'User-Agent': random_user_agent(),
                'Accept': 'text/html,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    )
    with urllib.request.urlopen(req) as response:
        return gzip.decompress(response.read()).decode('utf-8')


if __name__ == '__main__':
    pass
