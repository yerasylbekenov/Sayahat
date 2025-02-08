from flask import render_template, session

class UserController:
    def __init__(self, database):
        self.db = database

    def profile(self):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('profile.html', user=user)