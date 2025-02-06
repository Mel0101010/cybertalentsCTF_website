from flask import Flask, render_template, request, redirect, url_for, flash
import re

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'

CORRECT_ADDRESS = "7 Rue des Écoles Maligny"
CORRECT_PASSWORD = "P@ssw0rd123!"  # À modifier selon le mot de passe correct

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mission1', methods=['GET', 'POST'])
def mission1():
    if request.method == 'POST':
        adresse = request.form.get('adresse').strip()
        if adresse.lower() == CORRECT_ADDRESS.lower():
            flash('Félicitations! Vous avez trouvé la bonne adresse.', 'success')
            return redirect(url_for('mission2'))  # Redirection vers la mission suivante
        else:
            flash('Adresse incorrecte. Essayez encore.', 'error')
    return render_template('mission1.html')

@app.route('/mission2', methods=['GET', 'POST'])
def mission2():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CORRECT_PASSWORD:
            flash('Félicitations! Vous avez trouvé le mot de passe correct.', 'success')
            return redirect(url_for('mission3'))
        else:
            flash('Mot de passe incorrect. Essayez encore.', 'error')
    return render_template('mission2.html')


@app.route('/mission3', methods=['GET', 'POST'])
def mission3():
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag == "http://192.168.1.2":
            flash('Félicitations! Flag correct - Accès aux conversations obtenu.', 'success')
            return redirect(url_for('mission4'))  # Redirection vers la mission suivante
        else:
            flash('Flag incorrect. Essayez encore.', 'error')
    return render_template('mission3.html')

if __name__ == '__main__':
    app.run(debug=True)