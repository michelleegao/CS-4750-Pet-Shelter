from flask import Flask, render_template, request, redirect, url_for, flash
from db.connection import getconn
import uuid
from routes.families_routes import families_bp
## from db import mysql, db_connection, app
from routes.pets import pet_blueprint
from routes.events_routes import events_bp
from routes.login_route import login_bp
from routes.appointments import appointments_bp
from routes.users import users_blueprint
import os

app = Flask(__name__)


app.register_blueprint(appointments_bp)
app.register_blueprint(pet_blueprint)
app.register_blueprint(families_bp)
app.register_blueprint(events_bp)
app.register_blueprint(login_bp)
app.register_blueprint(users_blueprint)
app.config["SECRET KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key") # replace later with env var

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)