from flask import render_template, session, request, redirect, url_for

class PaymentsController:
    def __init__(self, database, ps):
        self.db = database
        self.ps = ps

    def payments(self):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('payer.html', user=user)
        
    def create_pslink(self):
        user_id = session['user_id']
        amount = request.form.get('amount')

        if not amount.isdigit():  # Проверяем, что строка состоит только из цифр
            return redirect(url_for('payments'))

        amount = int(amount)
        
        user = self.db.get_record('users', 'user_id', user_id)
        payment_result = self.ps.create_payment(amount=amount, currency='USD', description='Пополнение баланса')

        if payment_result.startswith("Платёж успешно создан! Перейдите по ссылке"):
            approval_url = payment_result.split(": ")[1]  # Извлекаем ссылку
            return redirect(approval_url)
        else:
            return redirect(url_for('payments'))


    def payment_success(self):
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')
        confirmation = self.ps.execute_payment(payment_id, payer_id)
        payment_status = paypal.get_payment_status(payment_id)
        return redirect(url_for('profile'))
