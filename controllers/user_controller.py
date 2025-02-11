from flask import render_template, session, request, redirect, url_for

class UserController:
    def __init__(self, database, uploader):
        self.db = database
        self.up = uploader

    def profile(self):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('profile.html', user=user)

    def up_photo(self):
        if 'avatar' not in request.files:
            return "Файл не найден", 400
        photo_url = request.files['avatar']
        user_id = session['user_id']
        response = self.up.upload_image(photo_url, "example.jpg")
        self.db.update_record('users', 'user_id', user_id, user_photo=response)
        return redirect(url_for('profile'))
        
