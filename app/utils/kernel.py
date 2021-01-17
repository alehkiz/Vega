from re import search
from dateutil.tz import tzutc
from babel.dates import format_timedelta
from functools import wraps
from datetime import datetime

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
        timestamp = timestamp.astimezone(tz=None)
        return format_timedelta(timestamp - datetime.now(tzutc()), add_direction=True)

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




