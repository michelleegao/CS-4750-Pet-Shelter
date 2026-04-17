from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from urllib.parse import quote_plus

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# load variables from .env for Google Cloud SQL
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
PROJECT_ID = os.getenv("PROJECT_ID")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")

encoded_password = quote_plus(DB_PASS)

# Flask config
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

print("DB_USER:", DB_USER)
print("DB_HOST:", DB_HOST)
print("DB_NAME:", DB_NAME)
print("DB_PASS loaded?", DB_PASS is not None)

@app.route("/test_db")
def test_db():
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return f"Database connection successful! Result: {result.scalar()}"
    except Exception as e:
        return f"Database connection failed: {e}"

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

# links family search HTML page
@app.route("/families")
def families():
    return render_template('families_search.html')

# links family view HTML page
@app.route("/families_view")
def families_view():
    return render_template('families_view.html')

# links family view HTML page
@app.route("/family_add")
def families_add():
    return render_template('addFamily.html')

if __name__ == "__main__":
    app.run(debug=True)