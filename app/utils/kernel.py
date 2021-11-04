import enum
from re import search
from dateutil.tz import tzutc
from babel.dates import format_timedelta, format_datetime, get_timezone
from functools import wraps
from datetime import datetime
from unicodedata import normalize, category
from werkzeug.urls import url_parse
from flask import request

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_123456789'
def validate_password(password):
    '''
    Valida uma senha com a regra:
    Senha deve conter mais que 6 caracteres;
    Senha deve conter um número
    Senha deve conter uma letra maiúscula
    Senha deve conter uma letra minúscula
    retorna um dicionário onde `ok` terá o resultado da validação com `True` se vaidado ou `False` se conter alguma inconsistêcnia
    '''
    valid_pass = {}
    valid_pass['length'] = len(password) >= 6
    valid_pass['digit'] = not search(r'\d', password) is None
    valid_pass['uppercase'] = not search(r'[A-Z]', password) is None
    valid_pass['lowercase'] = not search(r'[a-z]', password) is None
    # valid_pass['special_char'] = search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is not None
    valid_pass['ok'] = all(valid_pass.values())
    return valid_pass

def format_elapsed_time(timestamp):
    '''
    Retorna o tempo decorrido entre o ´timezone´ e tempo atual, retona no formato do tizone atual.
    '''
    if isinstance(timestamp, datetime):
        timestamp = timestamp.replace(microsecond=0)
        return format_timedelta(timestamp - datetime.utcnow(), add_direction=True, locale='pt_BR')

def format_datetime_local(timestamp, format='short'):
    if not format in ['full', 'long', 'medium', 'short']:
        format = 'short'
    if isinstance(timestamp, datetime):
        return format_datetime(timestamp, locale='pt_BR', format=format, tzinfo=get_timezone('America/Sao_Paulo'))

def get_list_max_len(l, max_value):
    '''
    Recebe uma lista ´l´ a retorna a mesma lista, desde que a quantidade de caracteres da lista não exceda ´max_value´
    '''
    if not isinstance(max_value, int) or max_value < 1:
        return l
    if sum([len(_) for _ in l]) < max_value:
        return l
    _temp_l = []
    _temp_sum = 0
    for v in l:
        _temp_sum += len(v)
        if _temp_sum > max_value:
            break
        _temp_l.append(v)
    if not _temp_l:
        return [l[0][0:max_value]]
    return _temp_l


def strip_accents(string:str):
    return ''.join(c for c in normalize('NFD', string)
                    if category(c)  != 'Mn')

def only_letters(string:str):
    text = strip_accents(string)
    text = text.replace(' ', '_')
    text = ''.join([x for x in text if x in ALPHABET])
    return text.lower()

def url_in_host(url):
    if url_parse(url).netloc == url_parse(request.base_url).netloc:
        return True
    return False


def order_dict(dictionary: dict, size:int =5, summarize=False,other_key:str='Outros', extra_size:bool=False):
    '''
    Ordena um dicionário recebido pelos valores, recorda de acordo com o `size` informado.
    insere os valores restantes em uma chave `other_key`
    '''

    _nd = dict(sorted(dictionary.items(), key= lambda item: item[1], reverse=True))
    agg = 0
    if summarize:
        if not extra_size:
            size = size-1
        for i, _d in enumerate(list(_nd.items())):
            if i >= size:
                agg += dictionary[_d[0]]
                _nd.pop(_d[0], None)

        if other_key in _nd.keys():
            agg += _nd[other_key]
            _nd[other_key] = agg
        else:
            _nd[other_key] = agg
        _nd = dict(sorted(_nd.items(), key= lambda item: item[1], reverse=True))
        return _nd

    for i, _d in enumerate(list(_nd.items())):
        if i >= size:
            _nd.pop(_d[0], None)
    return _nd


def format_number_as_thousand(number: int):
    return f'{number:,d}'.replace(',','.')