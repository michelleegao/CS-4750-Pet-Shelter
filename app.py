from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)



# User ORM for SQLAlchemy
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)

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