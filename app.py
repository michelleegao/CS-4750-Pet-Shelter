from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import text
# from urllib.parse import quote_plus
from db.connection import getconn
import uuid

app = Flask(__name__)
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

# links family search HTML page
@app.route("/families")
def families():
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT 
                        HEX(familyID) AS family_ID, 
                        first_name,
                        last_name
                       FROM families
                       ORDER by creation_date DESC, last_name ASC, first_name ASC
                       """)
        
        rows = cursor.fetchall()
        families_list = []
        for row in rows:
            families_list.append({
                "family_id": row[0],
                "first_name": row[1] or "",
                "last_name": row[2] or "",
                "photo_url": None
            })

        return render_template("families_search.html", families=families_list)

    except Exception as e:
        flash(f"Error loading families: {e}")
        return render_template("families_search.html", families=[])
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# links family view HTML page
@app.route("/families_view")
def families_view():
    return render_template('families_view.html')

# links family view HTML page
@app.route("/family_add", methods=["GET", "POST"])
def families_add():
    if request.method == "GET":
        return render_template('addFamily.html')

    conn = None
    cursor = None

    try:
        # base family fields
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        preferred_species = request.form.get("preferred_species")
        street = request.form.get("street")
        zip_code = request.form.get("zip_code")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        children = request.form.get("children")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        is_foster = request.form.get("is_foster") == "1"
        is_adoptive = request.form.get("is_adoptive") == "1"

        # subtype fields
        num_pets_fostered = request.form.get("num_pets_fostered")
        num_pets_owned = request.form.get("num_pets_owned")
        num_adults = request.form.get("num_adults")
        num_children = request.form.get("num_children")

        # basic validation
        if not first_name or not last_name:
            flash("First name and last name are required.")
            return redirect(url_for("families_add"))

        family_id = uuid.uuid4().bytes
        foster_family_id = uuid.uuid4().bytes if is_foster else None
        adoptive_family_id = uuid.uuid4().bytes if is_adoptive else None

        conn = getconn()
        cursor = conn.cursor()

        # insert into zip_code if not already there
        if zip_code:
            cursor.execute(""" INSERT INTO zip_codes (zip_code, city, state)
                           VALUES (%s, %s, %s)
                           ON DUPLICATE KEY UPDATE 
                                city = VALUES(city),
                                state = VALUES(state)
                           """, (zip_code, city, state))
            
        # insert into families    
        cursor.execute(""" INSERT INTO families (
                       familyID,
                       children,
                       street, 
                       zip_code,
                       country,
                       preferred_species,
                       first_name,
                       last_name,
                       num_occupants,
                       phone_number,
                       email,
                       creation_date
                       )
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                       """, (
                           family_id, 
                           int(children) if children is not None else None,
                           street or None,
                           int(zip_code) if zip_code else None,
                           country or None,
                           preferred_species or None,
                           first_name,
                           last_name,
                           None,
                           phone_number or None,
                           email or None
                       ))
        
        # insert adoptive subtype
        if is_adoptive:
            cursor.execute("""
                INSERT INTO adoptive_families (
                    familyID,
                    adoptive_family_ID,
                    num_pets_owned,
                    num_adults,
                    num_children
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                family_id,
                adoptive_family_id,
                int(num_pets_owned) if num_pets_owned else 0,
                int(num_adults) if num_adults else 0,
                int(num_children) if num_children else 0
            ))

        # insert foster subtype
        if is_foster:
            cursor.execute("""
                INSERT INTO foster_families (
                    familyID,
                    foster_family_ID,
                    num_pets_fostered
                )
                VALUES (%s, %s, %s)
            """, (
                family_id,
                foster_family_id,
                int(num_pets_fostered) if num_pets_fostered else 0
            ))

        conn.commit()
        flash("Family added successfully")
        return redirect(url_for("families"))
    
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error adding family: {e}")
        return redirect(url_for("families_add"))

    finally:
        if cursor:
            cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    app.run(debug=True)