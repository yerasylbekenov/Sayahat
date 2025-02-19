from flask import render_template, session, request, redirect, url_for
from datetime import datetime

class PurchasedController:
    def __init__(self, database):
        self.db = database

    def _format_tour_data(self, tour):
        """Helper method to format tour data for template"""
        # Get first photo from photos string (assuming it's comma-separated)
        photos = tour.photos.split(',')[0] if tour.photos else None
        
        # Parse the date strings into datetime objects if they're strings
        try:
            start_date = datetime.strptime(tour.start_date, '%Y-%m-%d %H:%M:%S') if isinstance(tour.start_date, str) else tour.start_date
            end_date = datetime.strptime(tour.end_date, '%Y-%m-%d %H:%M:%S') if isinstance(tour.end_date, str) else tour.end_date
            formatted_dates = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
        except (ValueError, TypeError):
            # Fallback if date parsing fails
            formatted_dates = f"{tour.start_date} - {tour.end_date}"
        
        return {
            'id': tour.tour_id,
            'image': photos,
            'status': tour.status,
            'title': tour.name,
            'date': formatted_dates,
            'price': f"{tour.price:,.0f}"
        }

    def main(self):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login'))

            # Get user information
            user = self.db.get_record('users', 'user_id', user_id)
            if not user:
                return redirect(url_for('login'))

            # Get all types of tours for the user
            active_tours = self.db.get_active_tours(user_id)
            upcoming_tours = self.db.get_upcoming_tours(user_id)

            # Format tour data for template
            purchased_tours = []
            
            # Add active tours
            for tour in active_tours:
                tour_data = self._format_tour_data(tour)
                purchased_tours.append(tour_data)

            # Add upcoming tours
            for tour in upcoming_tours:
                tour_data = self._format_tour_data(tour)
                purchased_tours.append(tour_data)

            # Calculate statistics
            stats = {
                'active_tours': len(active_tours),
                'upcoming_tours': len(upcoming_tours),
                'completed_tours': 0  # You might want to add a method to get completed tours
            }

            return render_template('purchased.html',
                                user=user,
                                purchased_tours=purchased_tours,
                                active_tours=stats['active_tours'],
                                upcoming_tours=stats['upcoming_tours'],
                                completed_tours=stats['completed_tours'])

        except Exception as e:
            # Log the error (you might want to add proper logging)
            print(f"Error in purchased controller: {e}")
            return redirect(url_for('login'))