from datetime import datetime
from os import remove
from flask import Blueprint, flash, render_template, redirect, url_for, current_app as app, request, abort, make_response, send_from_directory
from flask_login import login_required
from flask_security import login_required, current_user, roles_accepted
from app.forms.transaction import TransactionOptionForm, TransactionForm, TransactionOptionForm, TransactionScreenForm
from app.models.transactions import Transaction, TransactionOption, TransactionScreen
from app.utils.html import process_html
from app.utils.kernel import convert_datetime_to_local
from app.core.db import db
from os.path import join, isdir, isfile
from os import stat

from app.utils.routes import counter
bp = Blueprint('transaction', __name__, url_prefix='/transacoes')

@bp.route('/')
@bp.route('/index')
@login_required
@roles_accepted('admin', 'support')
def index():
    return 'none'

@bp.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def view(id : int):
    transaction = Transaction.query.filter(Transaction.id == id).first_or_404()
    
    return render_template('transaction.html', transaction_dict=transaction.to_dict)


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
            options_in_transaction = [x.option for x in transaction.options]
            if form.option.data in options_in_transaction:
                form.option.errors.append(f'Erro, {form.option.data} já está contido na transação {transaction.transaction}')
                return render_template('add.html', form=form, title='Adicionar Opções', options=True)
            option = TransactionOption()
            option.option = form.option.data
            option.description = process_html(form.description.data).text
            option.transaction_id = transaction.id
            db.session.add(option)
            try:
                db.session.add(option)
                db.session.commit()
                flash('Opção salva com sucesso', category="success")
                if request.form.get('save', False) == 'Salvar':
                    return redirect(url_for('transactions.add', id=transaction.id, screen=True))
                elif request.form.get('add', False) == 'Nova Opção':
                    return redirect(url_for('transactions.add', id=transaction.id, options=True))
                else:
                    return redirect(url_for('transactions.add', id=transaction.id, screen=True))
            except Exception as e:
                    app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
                    app.logger.error(e)
                    db.session.rollback()
                    return render_template('add.html', form=form, title='Adicionar', options=True)
        form.transaction.data = transaction.transaction
        return render_template('add.html', form=form, title='Adicionar Opções', options=True)
    if request.args.get('id', False) != False and request.args.get('screen', False) != False:
        form = TransactionScreenForm(request.form, tid=1)
        if not request.args.get('id', False).isnumeric():
            flash('Não foi possível identificar a transação', category='danger')
            return render_template('add.html', options=True)
        t_id = int(request.args.get('id', False))
        transaction = Transaction.query.filter(Transaction.id == t_id).first()
        if transaction is None:
            flash('Não foi possível identificar a transação', category='danger')
            return render_template('add.html', options=True)
        
        if form.validate_on_submit():
            files = request.files.getlist("files")
            for file in files:
                if file.filename != '':
                    if file.filename.split('.', 1)[1].lower() not in app.config['IMAGES_EXTENSION']:
                        form.files.errors.append(f"Arquivo não aceito, envie apenas arquivos no formato {', '.join(app.config['IMAGES_EXTENSION'])}")
                        return render_template('add.html', form=form, title='Adicionar Opções', screen=True)
                else:
                    form.files.errors.append(f"Nenhum arquivo enviado.")
                    return render_template('add.html', form=form, title='Adicionar Opções', screen=True)
                if isfile(join(app.config['UPLOAD_SCREEN_TRANSACTION_FOLDER'], file.filename)):
                    form.files.errors.append(f"Tela já existe.")
                    return render_template('add.html', form=form, title='Adicionar Opções', screen=True)
                
                screen = TransactionScreen.query.filter(TransactionScreen.filename.like(file.filename)).first()
                if screen is not None:
                    form.files.errors.append('Arquivo já existe')
                    return render_template('add.html', form=form, title='Adicionar Opções', screen=True)
                if form.transaction_option.data != '':
                    last_sequence = TransactionScreen.query.filter(TransactionScreen.transaction_id == form.transaction_option.data).order_by(TransactionScreen.id.desc()).limit(1).first()
                    last_sequence = last_sequence.screen_sequence if last_sequence != None else 0
                else:
                    last_sequence = 0
                screen = TransactionScreen()
                screen.active = True
                screen.screen_sequence = last_sequence + 1
                screen.uploaded_user_id = current_user.id
                screen.mimetype = file.mimetype
                screen.filename = file.filename
                screen.file_path = join(app.config['UPLOAD_SCREEN_TRANSACTION_FOLDER'], file.filename)
                screen.description = form.description.data
                screen.transaction_option_id = form.transaction_option.data
                screen.transaction_id = transaction.id
                file.save(screen.file_path)
                if not isfile(screen.file_path):
                    flash('Não foi possível salvar o arquivo', category='warning')
                    return render_template('add.html', form=form, title='Adicionar Opções', screen=True)
                size = stat(join(app.config['UPLOAD_SCREEN_TRANSACTION_FOLDER'], file.filename)).st_size
                screen.size = size
                try:
                    db.session.add(screen)
                    db.session.commit()
                    
                except Exception as e:
                        if isfile(screen.file_path):
                            remove(screen.file_path)
                            flash(f'Arquivo {file.filename} não existe {e}')
                            app.logger.error(f"Arquivo {file.path} não existe")
                            app.logger.error(e)
                            return abort(500)
                        app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
                        app.logger.error(e)
                        db.session.rollback()
                        return render_template('add.html', form=form, title='Adicionar', screen=True)
            if request.form.get('save') == 'Salvar':
                return redirect(url_for('transactions.view', id=transaction.id))
            elif request.form.get('add') == 'Nova Tela':
                return redirect(url_for('transactions.add', id=transaction.id, screen=True))
            else:
                return redirect(url_for('transactions.view', id=transaction.id))
            
        form.transaction.data = transaction.transaction
        return render_template('add.html', form=form, title='Adicionar Opções', screen=True)

    else:
    
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
                    return redirect(url_for('transactions.add', id=transaction.id, screen=True))
                elif request.form.get('prints') == 'Opções':
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


@bp.route('/deactive')
@login_required
@roles_accepted('admin', 'support')
def deactive():
    return 'none'

@bp.route('/active')
@login_required
@roles_accepted('admin', 'support')
def active():
    return 'none'

@bp.route('/screen/<int:id>')
def screen(id=None):
    if not id is None:
        file = TransactionScreen.query.filter(TransactionScreen.id == id).first_or_404()
        
        if not isfile(join(app.config['UPLOAD_SCREEN_TRANSACTION_FOLDER'], file.filename)):
            return abort(404)
        # binary_pdf = file.path
        response = make_response(send_from_directory(app.config['UPLOAD_SCREEN_TRANSACTION_FOLDER'], file.filename))
        
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = \
            f'inline; filename="{file.filename}";name="{file.filename}"'
        return response