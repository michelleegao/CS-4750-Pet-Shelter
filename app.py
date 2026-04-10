from flask import Flask, render_template

app = Flask(__name__)

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')

# links pets view HTML page
@app.route("/pets")
def pets():
    return render_template('pets_view.html')

if __name__ == "__main__":
    app.run(debug=True)