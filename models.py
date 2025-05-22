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
    current_chapter = db.Column(db.Integer, default=1)
    current_mission = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)

    # Relation avec les missions complétées
    completed_missions = db.relationship('CompletedMission', backref='user', lazy=True)
    # Relation avec les chapitres complétés
    completed_chapters = db.relationship('CompletedChapter', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def complete_mission(self, chapter_id, mission_id, points=10):
        # Vérifier si la mission a déjà été complétée
        already_completed = CompletedMission.query.filter_by(
            user_id=self.id, chapter_id=chapter_id, mission_id=mission_id).first()

        if not already_completed:
            # Ajouter la mission complétée
            completed = CompletedMission(user_id=self.id, chapter_id=chapter_id, mission_id=mission_id)
            db.session.add(completed)

            # Mettre à jour les points
            self.total_points += points
            
            # Mettre à jour la progression si c'est la mission actuelle du chapitre actuel
            if self.current_chapter == chapter_id and self.current_mission == mission_id:
                self.current_mission = mission_id + 1

            db.session.commit()
            return True
        return False

    def complete_chapter(self, chapter_id):
        # Vérifier si le chapitre a déjà été complété
        already_completed = CompletedChapter.query.filter_by(
            user_id=self.id, chapter_id=chapter_id).first()

        if not already_completed:
            # Ajouter le chapitre complété
            completed = CompletedChapter(user_id=self.id, chapter_id=chapter_id)
            db.session.add(completed)

            # Passer au chapitre suivant
            if self.current_chapter == chapter_id:
                self.current_chapter = chapter_id + 1
                self.current_mission = 1  # Recommencer à la mission 1 du nouveau chapitre

            db.session.commit()
            return True
        return False

    def is_chapter_unlocked(self, chapter_id):
        """Vérifie si un chapitre est débloqué pour l'utilisateur"""
        return chapter_id <= self.current_chapter

    def get_chapter_progress(self, chapter_id):
        """Retourne le nombre de missions complétées dans un chapitre"""
        return CompletedMission.query.filter_by(
            user_id=self.id, chapter_id=chapter_id).count()


class CompletedMission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chapter_id = db.Column(db.Integer, nullable=False)
    mission_id = db.Column(db.Integer, nullable=False)
    completed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'chapter_id', 'mission_id', name='_user_chapter_mission_uc'),)


class CompletedChapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chapter_id = db.Column(db.Integer, nullable=False)
    completed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'chapter_id', name='_user_chapter_uc'),)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Facile, Moyen, Difficile
    total_missions = db.Column(db.Integer, nullable=False)
    unlock_requirement = db.Column(db.Integer, default=0)  # Chapitre requis pour débloquer
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Chapter {self.title}>'