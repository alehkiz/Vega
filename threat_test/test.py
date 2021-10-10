from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
import requests
from werkzeug.urls import url_parse

import time

def get_url(url, cookie = ''):
    if cookie == '':
        raise Exception('Cookie vazio')
    try:
        return requests.get(url, cookies=cookie)
    except Exception as e:
        print('Erro')
        return ''

def thread_(url : str = '', number_exec : int = 100, cookie = ''):
    urls = [url] * number_exec
    cookies = [cookie] * number_exec
    with ThreadPoolExecutor(max_workers=200) as pool:
        return list(pool.map(get_url, urls, cookies))

def run_test(url : str = '', number_exec : int = 100):
    parsed_url = url_parse(url)
    scheme = parsed_url.scheme
    host = parsed_url.netloc

    cookie_url = f'{scheme}://{host}/select_access/Retaguarda'
    try:
        cookie = requests.get(cookie_url).cookies
    except Exception as e:
        print(e)
        time.sleep(2)
        try:
            cookie = requests.get(cookie_url).cookies
        except Exception as e:
            print('Erro')
            return 0
    if url == '':
        raise Exception('URL deve ser um texto')
    init_time = datetime.now()
    thread_(url=url, number_exec=number_exec, cookie= cookie)
    end_time = datetime.now()
    print('Tempo decorrido: ', end_time - init_time)
