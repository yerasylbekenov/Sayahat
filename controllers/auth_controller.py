from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps

class AuthController:
    def __init__(self, database, email_verifier):
        self.db = database
        self.email_verifier = email_verifier

    @staticmethod
    def login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Пожалуйста, войдите в систему для доступа к этой странице.')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapper

    def register(self):
        if request.method == 'POST':
            user_name = request.form['user_name']
            email = request.form['email']
            password = request.form['password']

            if self.db.get_user(email):
                flash('Пользователь с таким email уже существует.')
                return redirect(url_for('register'))

            if self.db.add_user(user_name=user_name, email=email, password=password):
                verification_code = self.email_verifier.send_verification_email(email, self.db)
                if verification_code:
                    flash('Код верификации отправлен на ваш email.')
                    return redirect(url_for('verify_code', email=email))
                flash('Ошибка при отправке кода верификации.')
                return redirect(url_for('register'))
            
            flash('Ошибка при регистрации.')
            return redirect(url_for('register'))

        return render_template('register.html')

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = self.db.get_user(email)
            if user and user.password == password:
                session['user_id'] = user.user_id
                flash('Вход выполнен успешно.')
                return redirect(url_for('index'))
            
            flash('Неверный email или пароль.')
            return redirect(url_for('login'))

        return render_template('login.html')

    def verify_email(self):
        if request.method == 'POST':
            email = request.form['email']
            verification_code = self.email_verifier.send_verification_email(email, self.db)
            if verification_code:
                flash('Код верификации отправлен на ваш email.')
                return redirect(url_for('verify_code', email=email))
            flash('Ошибка при отправке кода верификации.')
            return redirect(url_for('verify_email'))

        return render_template('verify_email.html')

    def verify_code(self, email):
        if request.method == 'POST':
            code = request.form['code']
            user = self.db.get_user(email)
            if user and user.code == code:
                session['user_id'] = user.user_id
                flash('Email успешно подтвержден.')
                return redirect(url_for('index'))
            flash('Неверный код верификации.')
            return redirect(url_for('verify_code', email=email))

        return render_template('verify_code.html', email=email)

    def logout(self):
        session.clear()
        flash('Вы успешно вышли из системы.')
        return redirect(url_for('login'))