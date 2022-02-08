import random
import time
from datetime import datetime
from dateutil import tz
from app.models.wiki import Question
from app.models.security import User
from app.core.db import db

def str_time_prop(start, end, format='%d-%m-%Y %H:%M:%S', prop=0):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date(start, end):
    return str_time_prop(start, end, '%d-%m-%Y %H:%M:%S', prop = random.random())


def convert_from_utc_to_local(utc):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Sao_Paulo')
    if utc is None or utc is False:
        return None     

    return utc.replace(tzinfo=from_zone).astimezone(to_zone)

def remove_answer(id:int):
    q = Question.query.filter(Question.id == id).first()
    if q is None:
        return False
    print(f'Pergunta: {q.question}')
    print(f'Respondido por: {User.query.filter(User.id == q.answer_user_id).first().name}')
    print(f'Resposta: {q.answer}')
    answer = input('Tem certeza que deseja excluir a resposta? s(Sim) n(Não):')
    if answer == 's':
        if not q.was_approved:
            q.answer = None
            q.answer_at = None
            q.answer_network_id = None
            q.answer_user_id = None
            db.session.commit()
            print(f'Removida a resposta da pergunta {q.id}')
        else:
            print('Pergunta já aprovada, não é possível remover a resposta.')

    elif answer == 'n':
        print(f'Nenhuma atualização para a pergunta {q.id}')

def remove_question(id:int):
    q = Question.query.filter(Question.id == id).first()
    if q is None:
        return False
    print(f'Pergunta: {q.question}')
    print(f'Respondido por: {User.query.filter(User.id == q.answer_user_id).first().name}')
    print(f'Resposta: {q.answer}')
    answer = input('Tem certeza que deseja excluir a pergunta? s(Sim) n(Não):')
    if answer == 's':
        if not q.was_approved:
            db.session.delete(q)
            db.session.commit()
            print(f'Removida a pergunta {q.id}')
        else:
            print('Pergunta já aprovada, não é possível remover a pergunta.')

    elif answer == 'n':
        print(f'Nenhuma atualização para a pergunta {q.id}')