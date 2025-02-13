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
  

@app.route('/mission4', methods=['GET', 'POST'])
def mission4():
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag.lower() == "random.pyc":
            flash('Félicitations! Vous avez trouvé le fichier binaire correct.', 'success')
            return redirect(url_for('mission5'))  # Redirection vers mission5
        else:
            flash('Nom de fichier incorrect. Continuez votre recherche.', 'error')
    return render_template('mission4.html', success=False)

@app.route('/mission5', methods=['GET', 'POST'])
def mission5():
    if request.method == 'POST':
        flag = request.form.get('flag')
        if flag.upper() == "FLAG{RANDOMAM}":
            flash('Félicitations! Vous avez trouvé le flag correct!', 'success')
            return redirect(url_for('mission6'))  # Redirection vers mission6
        else:
            flash('Flag incorrect. Continuez votre analyse.', 'error')
    return render_template('mission5.html')

@app.route('/mission6', methods=['GET', 'POST'])
def mission6():
    if request.method == 'POST':
        filename = request.form.get('filename')
        if filename.lower() == "server.py":  # Le nom du fichier à trouver
            flash('Félicitations! Vous avez identifié le bon fichier dans la capture réseau.', 'success')
            return redirect(url_for('victory'))  # Redirection vers la page de victoire
        else:
            flash('Nom de fichier incorrect. Continuez votre analyse.', 'error')
    return render_template('mission6.html')

@app.route('/mission7', methods=['GET', 'POST'])
def mission7():
    if request.method == 'POST':
        secret_key = request.form.get('secret_key')
        if secret_key == "Cr4ck3d!":  # La clé secrète à trouver
            flash('Félicitations! Vous avez découvert la clé secrète!', 'success')
            return redirect(url_for('mission8'))  # Redirection vers mission6
        else:
            flash('Clé incorrecte. Continuez vos recherches.', 'error')
    return render_template('mission7.html')


if __name__ == '__main__':
    app.run(debug=True)