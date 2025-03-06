from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    current_mission = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)

    # Relation avec les missions complétées
    completed_missions = db.relationship('CompletedMission', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def complete_mission(self, mission_id, points=10):
        # Vérifier si la mission a déjà été complétée
        already_completed = CompletedMission.query.filter_by(
            user_id=self.id, mission_id=mission_id).first()

        if not already_completed:
            # Ajouter la mission complétée
            completed = CompletedMission(user_id=self.id, mission_id=mission_id)
            db.session.add(completed)

            # Mettre à jour les points et la mission actuelle
            self.total_points += points
            if self.current_mission == mission_id:
                self.current_mission = mission_id + 1

            db.session.commit()
            return True
        return False


class CompletedMission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mission_id = db.Column(db.Integer, nullable=False)
    completed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'mission_id', name='_user_mission_uc'),)