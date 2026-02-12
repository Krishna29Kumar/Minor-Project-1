from flask import Flask, render_template, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
import os

app = Flask(__name__)

# ==========================
# CONFIGURATION
# ==========================

app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///innervoice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

client = OpenAI()

# ==========================
# DATABASE MODELS
# ==========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    quiz_completed = db.Column(db.Boolean, default=False)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    response = db.Column(db.Text)


# ==========================
# BASIC ROUTES
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/wellbeing")
def wellbeing():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("wellbeing.html")


@app.route("/chatbot")
def chatbot():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("chatbot.html")


# ==========================
# AUTHENTICATION
# ==========================

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    if User.query.filter_by(email=email).first():
        return "Email already registered"

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return redirect("/quiz")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id

        if user.quiz_completed:
            return redirect("/dashboard")
        else:
            return redirect("/quiz")
    else:
        return "Invalid credentials"


# ==========================
# QUIZ SYSTEM
# ==========================

@app.route("/quiz")
def quiz():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if user.quiz_completed:
        return redirect("/dashboard")

    return render_template("children.html")


@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    user.quiz_completed = True
    db.session.commit()

    return redirect("/dashboard")


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if not user.quiz_completed:
        return redirect("/quiz")

    return render_template("dashboard.html", name=user.name)


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
