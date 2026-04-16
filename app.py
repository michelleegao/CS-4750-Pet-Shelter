from flask import Flask, render_template

app = Flask(__name__)

# links login HTML page
@app.route("/")
def home():
    return render_template('login.html')

# links pets search HTML page
@app.route("/pets_search")
def pets():
    return render_template('/templates/pets_search.html')

# links pets view HTML page
@app.route("/pets_view")
def pets_view():
    return render_template('/templates/pets_view.html')

if __name__ == "__main__":
    app.run(debug=True)