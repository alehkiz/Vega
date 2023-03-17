from datetime import datetime
from flask import Blueprint, flash, render_template, redirect, url_for, current_app as app, request
from flask_login import login_required
from flask_security import login_required, current_user, roles_accepted
from app.forms.transaction import TransactionForm, TransactionOptionForm, TransactionScreenForn
from app.models.transactions import Transaction, TransactionOption
from app.utils.kernel import convert_datetime_to_local
from app.core.db import db

from app.utils.routes import counter
bp = Blueprint('transactions', __name__, url_prefix='/transacoes')

@bp.route('/')
@bp.route('/index')
@login_required
@roles_accepted('admin', 'support')
def index():
    return 'none'


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def add():
    if request.args.get('id', False) != False and request.args.get('options', False) != False:
        form = TransactionOptionForm()
        if not request.args.get('id', False).isnumeric():
            flash('Não foi possível identificar a transação', category='danger')
            return render_template('add.html', options=True)
        t_id = int(request.args.get('id', False))
        transaction = Transaction.query.filter(Transaction.id == t_id).first()
        if transaction is None:
            flash('Não foi possível identificar a transação', category='danger')
            return render_template('add.html', options=True)
        
        if form.validate_on_submit():
            
            option = TransactionOption()
            print(form.options)
        form.transaction.data = transaction.transaction
        return render_template('add.html', form=form, title='Adicionar', options=True)
    
    
    
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction.query.filter(Transaction.transaction.ilike(form.transaction.data)).first()
        if transaction != None:
            # flash(f'Transação {form.transaction.data} já está cadastrada.', category='danger')
            form.transaction.errors.append(f'Transação {form.transaction.data} já está cadastrada.')
            return render_template('add.html', form=form, title='Adicionar', transaction=True)            
        transaction = Transaction()
        transaction.transaction = form.transaction.data
        transaction.parameters.extend(form.parameter.data)
        transaction.description = form.description.data
        transaction.type_id = form.type.data[0].id
        transaction.topics.extend(form.topic.data)
        transaction.sub_topics.extend(form.sub_topics.data)
        transaction.created_user_id = current_user.id
        transaction.create_at = convert_datetime_to_local(datetime.utcnow())

        try:
            db.session.add(transaction)
            db.session.commit()
            if request.form.get('submit') == 'Salvar':
                return redirect(url_for('transactions.id', id=transaction.id))
            elif request.form.get('submit') == 'Prints':
                return redirect(url_for('transactions.add', id=transaction.id, options=True))
            else:
                return redirect(url_for('transactions.add', id=transaction.id, options=True))
        except Exception as e:
                app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Adicionar', transaction=True)

    return render_template('add.html', form=form, title='Adicionar', transaction=True)

@bp.route('/edit')
@login_required
@roles_accepted('admin', 'support')
def edit():
    return 'none'