from flask import Flask, render_template
## from db import mysql, db_connection, app
from routes.pets import pet_blueprint

app = Flask(__name__)

app.register_blueprint(pet_blueprint)

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)