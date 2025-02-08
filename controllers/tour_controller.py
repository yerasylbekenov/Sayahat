from flask import render_template, jsonify, session

class TourController:
    def __init__(self, database):
        self.db = database

    def index(self):
        tours = self.db.get_all_tours()
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('index.html', user=user, tours=tours)

    def search(self, search_term):
        tours = self.db.search_tours(search_term) if search_term else self.db.get_all_tours()
        return jsonify([tour.__dict__ for tour in tours])

    def purchased(self):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('purchased.html', user=user)
