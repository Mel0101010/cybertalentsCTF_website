from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from datetime import datetime
import secrets

# Import des modèles
from models import db, User, CompletedMission, CompletedChapter, Chapter

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

# Configuration des chapitres et missions
CHAPTERS_CONFIG = {
    1: {
        'title': 'Investigation Criminelle',
        'description': 'Enquête sur un suspect et analyse forensique',
        'difficulty': 'Facile',
        'missions': 8,
        'answers': {
            1: "7 Rue des Écoles Maligny",
            2: "P@ssw0rd123!",
            3: "http://192.168.1.2",
            4: "random.pyc",
            5: "FLAG{RANDOMAM}",
            6: "server.py",
            7: "Cr4ck3d!",
            8: "32-rue-herge"
        }
    },
    2: {
        'title': 'Challenges de Programmation',
        'description': 'Une série de défis de programmation pour tester vos compétences',
        'difficulty': 'Moyen',
        'missions': 15,
        'answers': {
            1: "FLAG{W3LC0M3_C4ND1D4T3_F1R5T_T35T_P4553D}",
            2: "FLAG{B451C_M4TH_5K1LL5_C0NF1RM3D}",
            3: "FLAG{D1G1T4L_L4NGU4G3_UND3R5T00D}",
            4: "FLAG{L1NGU15T1C_4N4LY515_C0MPL3T3D}",
            5: "FLAG{P0L15H_N0T4T10N_M45T3R3D}",
            6: "FLAG{D3DUC7ION_4ND_L0G1C_PR0V3N}",
            7: "FLAG{4NC13NT_C1PH3R5_D3CRY7T3D_W3LC0M3_4G3NT}",
            8: "FLAG{D4T4_P4R51NG_3XP3RT153_4CQU1R3D}",
            9: "FLAG{5T34LTH_D4T4_H4NDL1NG_4PPR0V3D}",
            10: "FLAG{P4TT3RN_R3C0GN1T10N_5P3C14L15T}",
            11: "FLAG{50C_4N4LY5T_L3V3L_R34CH3D}",
            12: "FLAG{0P3R4T10N4L_3FF1C13NCY_M4X1M1Z3D}",
            13: "FLAG{4G3NT_R35CU3_M1551ON_5UCC355FUL}",
            14: "FLAG{HUM4N_V3R1F1C4T10N_BY7P4553D}",
            15: "FLAG{53CUR3_C0MMUN1C4T10N_M45T3R_4G3NT_001}"
        }
    }
}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Création de la base de données et des chapitres par défaut
with app.app_context():
    db.create_all()
    
    # Créer les chapitres s'ils n'existent pas
    for chapter_id, config in CHAPTERS_CONFIG.items():
        existing_chapter = Chapter.query.filter_by(id=chapter_id).first()
        if not existing_chapter:
            chapter = Chapter(
                id=chapter_id,
                title=config['title'],
                description=config['description'],
                difficulty=config['difficulty'],
                total_missions=config['missions'],
                unlock_requirement=chapter_id - 1 if chapter_id > 1 else 0
            )
            db.session.add(chapter)
    
    db.session.commit()


# Décorateur pour vérifier l'accès aux chapitres et missions
def chapter_access_required(chapter_id):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            if not current_user.is_chapter_unlocked(chapter_id):
                flash(f"Vous devez compléter le chapitre {chapter_id - 1} pour accéder à ce contenu.", "error")
                return redirect(url_for('chapters'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def mission_access_required(chapter_id_param, mission_id_param):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            # Get the actual values from kwargs
            chapter_id = kwargs.get(chapter_id_param)
            mission_id = kwargs.get(mission_id_param)

            if not chapter_id or not mission_id:
                abort(404)

            # Vérifier l'accès au chapitre
            if not current_user.is_chapter_unlocked(chapter_id):
                flash(f"Vous devez compléter le chapitre {chapter_id - 1} pour accéder à ce contenu.", "error")
                return redirect(url_for('chapters'))

            # Vérifier l'accès à la mission dans le chapitre actuel
            if current_user.current_chapter == chapter_id and current_user.current_mission < mission_id:
                flash("Vous devez compléter les missions précédentes d'abord.", "error")
                return redirect(url_for('mission', chapter_id=chapter_id, mission_id=current_user.current_mission))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes d'authentification (identiques à l'original)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

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


# Pages principales
@app.route('/')
def home():
    chapters = Chapter.query.order_by(Chapter.id).all()
    return render_template('index.html', chapters=chapters)


@app.route('/chapters')
@login_required
def chapters():
    chapters = Chapter.query.order_by(Chapter.id).all()
    user_progress = {}
    
    for chapter in chapters:
        user_progress[chapter.id] = {
            'unlocked': current_user.is_chapter_unlocked(chapter.id),
            'completed_missions': current_user.get_chapter_progress(chapter.id),
            'total_missions': chapter.total_missions
        }
    
    return render_template('chapters.html', chapters=chapters, user_progress=user_progress)


@app.route('/scoreboard')
def scoreboard():
    users = User.query.order_by(User.total_points.desc()).all()
    return render_template('scoreboard.html', users=users)


# Routes des missions génériques
@app.route('/chapter/<int:chapter_id>/mission/<int:mission_id>', methods=['GET', 'POST'])
@login_required
@mission_access_required('chapter_id', 'mission_id')
def mission(chapter_id, mission_id):
    # Vérifier que le chapitre et la mission existent
    if chapter_id not in CHAPTERS_CONFIG:
        abort(404)
    
    chapter_config = CHAPTERS_CONFIG[chapter_id]
    if mission_id > chapter_config['missions']:
        abort(404)

    if request.method == 'POST':
        # Récupérer la réponse selon le type de mission
        answer_key = list(request.form.keys())[0] if request.form else None
        user_answer = request.form.get(answer_key, '').strip()
        
        correct_answer = chapter_config['answers'].get(mission_id)
        
        if user_answer.lower() == correct_answer.lower():
            success = current_user.complete_mission(chapter_id, mission_id, 10)
            if success:
                flash(f'Félicitations! Mission {mission_id} complétée. (+10 points)', 'success')
                
                # Vérifier si c'est la dernière mission du chapitre
                if mission_id == chapter_config['missions']:
                    current_user.complete_chapter(chapter_id)
                    flash(f'Chapitre {chapter_id} terminé! Nouveau chapitre débloqué!', 'success')
                    return redirect(url_for('chapters'))
                else:
                    return redirect(url_for('mission', chapter_id=chapter_id, mission_id=mission_id + 1))
        else:
            flash('Réponse incorrecte. Essayez encore.', 'error')

    # Charger le template spécifique à la mission
    template_name = f'chapter{chapter_id}/mission{mission_id}.html'
    try:
        return render_template(template_name, chapter_id=chapter_id, mission_id=mission_id)
    except:
        # Template par défaut si le fichier spécifique n'existe pas
        return render_template('mission_template.html', 
                             chapter_id=chapter_id, 
                             mission_id=mission_id,
                             chapter_title=chapter_config['title'])


# Routes pour les anciennes missions (compatibilité)
@app.route('/mission1', methods=['GET', 'POST'])
@login_required
def mission1():
    return redirect(url_for('mission', chapter_id=1, mission_id=1))

@app.route('/mission2', methods=['GET', 'POST'])
@login_required
def mission2():
    return redirect(url_for('mission', chapter_id=1, mission_id=2))

@app.route('/mission3', methods=['GET', 'POST'])
@login_required
def mission3():
    return redirect(url_for('mission', chapter_id=1, mission_id=3))

# ... (ajouter les autres redirections si nécessaire)


# Page de victoire
@app.route('/victory')
@login_required
def victory():
    total_chapters = len(CHAPTERS_CONFIG)
    if current_user.current_chapter <= total_chapters:
        flash("Terminez tous les chapitres pour accéder à cette page.", "error")
        return redirect(url_for('chapters'))

    return render_template('victory.html')


# Page d'erreur 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run("0.0.0.0", 8000, debug=True)