from re import search

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
