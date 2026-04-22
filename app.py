from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import text
# from urllib.parse import quote_plus
from db.connection import getconn
import uuid
from routes.families_routes import families_bp

app = Flask(__name__)
app.register_blueprint(families_bp)
app.secret_key = "dev-secret-key" # replace later with env var

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')

# links pets search HTML page
@app.route("/pets")
def pets():
    return render_template('pets_search.html')

# links pets view HTML page
@app.route("/pets_view")
def pets_view():
    return render_template('pets_view.html')


if __name__ == "__main__":
    app.run(debug=True)