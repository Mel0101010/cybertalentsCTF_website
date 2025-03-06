from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from datetime import datetime
import secrets

# Import des modèles
from models import db, User, CompletedMission

# Configuration de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Vous devez être connecté pour accéder à cette page."
login_manager.login_message_category = "error"

# Réponses correctes pour chaque mission
MISSION_ANSWERS = {
    1: "7 Rue des Écoles Maligny",  # Mission 1: Adresse
    2: "P@ssw0rd123!",  # Mission 2: Mot de passe
    3: "http://192.168.1.2",  # Mission 3: Flag
    4: "random.pyc",  # Mission 4: Nom du fichier
    5: "FLAG{RANDOMAM}",  # Mission 5: Flag
    6: "server.py",  # Mission 6: Nom du fichier
    7: "Cr4ck3d!"  # Mission 7: Clé secrète
}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Création de la base de données si elle n'existe pas
# Dans les versions récentes de Flask, before_first_request est déprécié
# Utilisons une approche différente
with app.app_context():
    db.create_all()


# Décorateur pour vérifier l'accès à la mission
def mission_access_required(mission_id):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            # Vérifier si l'utilisateur a accès à cette mission
            if current_user.current_mission < mission_id:
                flash("Vous devez compléter les missions précédentes d'abord.", "error")
                return redirect(url_for(f'mission{current_user.current_mission}'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Routes d'authentification
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Vérifications des données
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
        elif email_exists:
            flash('Cet email est déjà utilisé.', 'error')
        elif password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
        elif len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
        else:
            # Création du nouvel utilisateur
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Connexion réussie!', 'success')
            return redirect(next_page or url_for('home'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('home'))


# Page d'accueil
@app.route('/')
def home():
    return render_template('index.html')


# Tableau des scores
@app.route('/scoreboard')
def scoreboard():
    # Récupérer tous les utilisateurs triés par points
    users = User.query.order_by(User.total_points.desc()).all()
    return render_template('scoreboard.html', users=users)


# Routes des missions
@app.route('/mission1', methods=['GET', 'POST'])
@login_required
def mission1():
    if request.method == 'POST':
        adresse = request.form.get('adresse').strip()
        if adresse.lower() == MISSION_ANSWERS[1].lower():
            # Marquer la mission comme complétée
            current_user.complete_mission(1, 10)

            flash('Félicitations! Vous avez trouvé la bonne adresse. (+10 points)', 'success')
            return redirect(url_for('mission2'))
        else:
            flash('Adresse incorrecte. Essayez encore.', 'error')

    return render_template('mission1.html')


@app.route('/mission2', methods=['GET', 'POST'])
@login_required
@mission_access_required(2)
def mission2():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == MISSION_ANSWERS[2]:
            # Marquer la mission comme complétée
            current_user.complete_mission(2, 10)

            flash('Félicitations! Vous avez trouvé le mot de passe correct. (+10 points)', 'success')
            return redirect(url_for('mission3'))
        else:
            flash('Mot de passe incorrect. Essayez encore.', 'error')

    return render_template('mission2.html')


@app.route('/mission3', methods=['GET', 'POST'])
@login_required
@mission_access_required(3)
def mission3():
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag == MISSION_ANSWERS[3]:
            # Marquer la mission comme complétée
            current_user.complete_mission(3, 10)

            flash('Félicitations! Flag correct - Accès aux conversations obtenu. (+10 points)', 'success')
            return redirect(url_for('mission4'))
        else:
            flash('Flag incorrect. Essayez encore.', 'error')

    return render_template('mission3.html')


@app.route('/mission4', methods=['GET', 'POST'])
@login_required
@mission_access_required(4)
def mission4():
    success = False
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag.lower() == MISSION_ANSWERS[4].lower():
            # Marquer la mission comme complétée
            current_user.complete_mission(4, 10)

            flash('Félicitations! Vous avez trouvé le fichier binaire correct. (+10 points)', 'success')
            success = True
            return redirect(url_for('mission5'))
        else:
            flash('Nom de fichier incorrect. Continuez votre recherche.', 'error')

    return render_template('mission4.html', success=success)


@app.route('/mission5', methods=['GET', 'POST'])
@login_required
@mission_access_required(5)
def mission5():
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag.upper() == MISSION_ANSWERS[5].upper():
            # Marquer la mission comme complétée
            current_user.complete_mission(5, 10)

            flash('Félicitations! Vous avez trouvé le flag correct! (+10 points)', 'success')
            return redirect(url_for('mission6'))
        else:
            flash('Flag incorrect. Continuez votre analyse.', 'error')

    return render_template('mission5.html')


@app.route('/mission6', methods=['GET', 'POST'])
@login_required
@mission_access_required(6)
def mission6():
    if request.method == 'POST':
        filename = request.form.get('filename')
        if filename.lower() == MISSION_ANSWERS[6].lower():
            # Marquer la mission comme complétée
            current_user.complete_mission(6, 10)

            flash('Félicitations! Vous avez identifié le bon fichier dans la capture réseau. (+10 points)', 'success')
            return redirect(url_for('mission7'))
        else:
            flash('Nom de fichier incorrect. Continuez votre analyse.', 'error')

    return render_template('mission6.html')


@app.route('/mission7', methods=['GET', 'POST'])
@login_required
@mission_access_required(7)
def mission7():
    if request.method == 'POST':
        secret_key = request.form.get('secret_key')
        if secret_key == MISSION_ANSWERS[7]:
            # Marquer la mission comme complétée
            current_user.complete_mission(7, 10)

            flash('Félicitations! Vous avez découvert la clé secrète! (+10 points)', 'success')
            return redirect(url_for('victory'))
        else:
            flash('Clé incorrecte. Continuez vos recherches.', 'error')

    return render_template('mission7.html')


# Page de victoire après complétion de toutes les missions
@app.route('/victory')
@login_required
def victory():
    # Vérifier si l'utilisateur a terminé toutes les missions
    if current_user.current_mission < 8:
        flash("Terminez toutes les missions pour accéder à cette page.", "error")
        return redirect(url_for(f'mission{current_user.current_mission}'))

    return render_template('victory.html')


# Page d'erreur 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)