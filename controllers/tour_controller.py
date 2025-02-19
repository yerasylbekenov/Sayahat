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

    def tour_details(self, tour_id):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        tour = self.db.get_record('tours', 'tour_id', tour_id)
        if not tour:
            return "Тур не найден", 404
        
        # Получаем список городов из поля cities
        cities = []
        if hasattr(tour, 'cities') and tour.cities:
            city_names = tour.cities.split(',')  # Предположим, что города разделены запятыми
            for city_name in city_names:
                city = self.db.get_record('cities', 'name', city_name.strip())
                if city:
                    cities.append(city)
        
        return render_template('tour.html', tour=tour, cities=cities, user=user)

    def purchase_tour(self, tour_id):
        tour = self.db.get_record('tours', 'tour_id', tour_id)
        if not tour:
            return "Тур не найден", 404
        return render_template('purchase.html', tour=tour)