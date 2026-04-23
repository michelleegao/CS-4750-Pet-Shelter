from flask import Flask, render_template, request, redirect, url_for, flash
from db.connection import getconn
import uuid
from routes.families_routes import families_bp
## from db import mysql, db_connection, app
from routes.pets import pet_blueprint

app = Flask(__name__)

app.register_blueprint(pet_blueprint)
app.register_blueprint(families_bp)
app.secret_key = "dev-secret-key" # replace later with env var

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)