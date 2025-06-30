from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import auth, db

# Inicializar Firebase Admin SDK
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = "villavicencio"  # Clave secreta para sesiones

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Simulación simple de usuarios en memoria
users = {
    "user1": {"id": "user1", "username": "Usuario1", "email": "user1@example.com", "password": "1234", "registered_on": datetime(2025,5,31)},
    # Puedes agregar más usuarios aquí o conectar a Firebase Auth u otra base
}

class User(UserMixin):
    def __init__(self, id, username, email, registered_on):
        self.id = id
        self.username = username
        self.email = email
        self.registered_on = registered_on


@login_manager.user_loader
def load_user(user_id):
    user_data = users.get(user_id)
    if user_data:
        return User(user_data["id"], user_data["username"], user_data["email"], user_data["registered_on"])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']

            # Agregar usuario a Flask-Login
            user_id = user['localId']
            user_obj = User(id=user_id, username=email.split("@")[0], email=email, registered_on=datetime.now())
            users[user_id] = {
                "id": user_id,
                "username": user_obj.username,
                "email": user_obj.email,
                "registered_on": user_obj.registered_on
            }
            login_user(user_obj)

            return redirect(url_for('home'))
        except Exception as e:
            flash('Error al iniciar sesión: ' + str(e))
    return render_template('login.html')



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.pop('user', None)
    flash('Has cerrado sesión.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            flash('Registro exitoso. Inicia sesión.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error en el registro: ' + str(e))
    return render_template('register.html')

@app.route("/home")
@login_required
def home():
    user = current_user.username

    # Manejo de racha (si quieres mantenerlo)
    today = datetime.now().date()
    last_visit_str = session.get("last_visit")
    streak = session.get("streak", 0)

    if last_visit_str:
        last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d").date()
        days_diff = (today - last_visit).days

        if days_diff == 1:
            streak += 1
        elif days_diff > 1:
            streak = 1
    else:
        streak = 1

    session["last_visit"] = today.strftime("%Y-%m-%d")
    session["streak"] = streak

    return render_template("home.html", user=user, streak=streak)

@app.route("/plants", methods=["GET", "POST"])
def plants():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    docs = db.collection("plants").stream()
    all_plants = [doc.to_dict() for doc in docs]

    if request.method == "POST":
        selected = request.form.getlist("selected_plants")
        main_plant = request.form.get("main_plant")
        session["my_plants"] = selected
        session["main_plant"] = main_plant
        return redirect(url_for("my_plants"))

    return render_template("plants.html", plants=all_plants)


@app.route("/my_plants", methods=["GET", "POST"])
@login_required
def my_plants():
    selected_plants = session.get("my_plants", [])
    if not selected_plants:
        return redirect(url_for("plants"))

    if request.method == "POST":
        # ✅ Verifica si se presionó el botón de regar
        planta_regada = request.form.get("watered")
        if planta_regada:
            db.collection("plants").document(planta_regada).update({
                "last_watering_date": datetime.now().strftime("%Y-%m-%d")
            })
            flash(f"Has regado {planta_regada}.")
            return redirect(url_for("my_plants"))

    plants_details = []
    for name in selected_plants:
        doc = db.collection("plants").document(name).get()
        if doc.exists:
            data = doc.to_dict()
            last_watering_str = data.get("last_watering_date")
            if last_watering_str:
                last_watering_date = datetime.strptime(last_watering_str, "%Y-%m-%d")
            else:
                last_watering_date = datetime.now() - timedelta(days=10)
            days_since_watering = (datetime.now() - last_watering_date).days
            needs_watering = days_since_watering >= data["riego_cada_dias"]

            plants_details.append({
                "nombre": data["nombre"],
                "riego_cada_dias": data["riego_cada_dias"],
                "luz": data["luz"],
                "needs_watering": needs_watering,
                "days_since_watering": days_since_watering,
                "last_watering_date": last_watering_date.strftime("%Y-%m-%d"),
            })

    return render_template("my_plants.html", plants=plants_details)


@app.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
