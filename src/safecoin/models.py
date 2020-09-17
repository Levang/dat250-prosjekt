from safecoin import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

<<<<<<< HEAD
class User(db.Model, UserMixin):
=======
class User(db.Model):
>>>>>>> 4b5c0c9e72be70ee1b00659b11035b7d09d3a269
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(60), nullable=False)
