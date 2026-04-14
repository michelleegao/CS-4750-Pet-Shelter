from flask import Flask, render_template

app = Flask(__name__)

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