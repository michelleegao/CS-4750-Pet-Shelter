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

        cursor.execute("SELECT DATABASE()")
        print("CURRENT DB:", cursor.fetchone())

        cursor.execute("SELECT COUNT(*) FROM families")
        print("FAMILY COUNT:", cursor.fetchone())

        cursor.execute("""
            SELECT 
                HEX(familyID) AS family_ID, 
                first_name,
                last_name
            FROM families
            ORDER BY creation_date DESC, last_name ASC, first_name ASC
        """)

        rows = cursor.fetchall()
        print("ROWS:", rows)

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
        print("ERROR IN /families:", e)
        return f"Error loading families: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# links family view HTML page
@app.route("/families/<family_id>")
def families_view(family_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                HEX(f.familyID) AS family_id,
                f.first_name,
                f.last_name,
                f.preferred_species,
                f.children,
                f.street,
                f.zip_code,
                z.city,
                z.state,
                f.country,
                f.num_occupants,
                f.phone_number,
                f.email,
                af.num_pets_owned,
                af.num_adults,
                af.num_children,
                ff.num_pets_fostered
            FROM families f
            LEFT JOIN zip_codes z ON f.zip_code = z.zip_code
            LEFT JOIN adoptive_families af ON f.familyID = af.familyID
            LEFT JOIN foster_families ff ON f.familyID = ff.familyID
            WHERE HEX(f.familyID) = %s
        """, (family_id,))

        row = cursor.fetchone()

        if not row:
            flash("Family not found.")
            return redirect(url_for("families"))

        family = {
            "family_id": row[0],
            "first_name": row[1] or "",
            "last_name": row[2] or "",
            "preferred_species": row[3] or "",
            "children": row[4],
            "street": row[5] or "",
            "zip_code": row[6] or "",
            "city": row[7] or "",
            "state": row[8] or "",
            "country": row[9] or "",
            "num_occupants": row[10],
            "phone_number": row[11] or "",
            "email": row[12] or "",
            "num_pets_owned": row[13],
            "num_adults": row[14],
            "num_children": row[15],
            "num_pets_fostered": row[16],
            "photo_url": None
        }

        return render_template("families_view.html", family=family)

    except Exception as e:
        print("ERROR IN /families/<family_id>:", e)
        return f"Error loading family: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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

# edit families
@app.route("/families/<family_id>/edit", methods=["POST"])
def edit_family(family_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        preferred_species = request.form.get("preferred_species", "").strip()
        children = request.form.get("children", "").strip()
        street = request.form.get("street", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        country = request.form.get("country", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        email = request.form.get("email", "").strip()

        num_adults = request.form.get("num_adults", "").strip()
        num_children = request.form.get("num_children", "").strip()
        num_pets_owned = request.form.get("num_pets_owned", "").strip()
        num_pets_fostered = request.form.get("num_pets_fostered", "").strip()

        if zip_code:
            cursor.execute("""
                INSERT INTO zip_codes (zip_code, city, state)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    city = COALESCE(NULLIF(VALUES(city), ''), city),
                    state = COALESCE(NULLIF(VALUES(state), ''), state)
            """, (
                int(zip_code),
                city if city else None,
                state if state else None
            ))

        family_updates = []
        family_values = []

        if preferred_species:
            family_updates.append("preferred_species = %s")
            family_values.append(preferred_species)

        if children != "":
            family_updates.append("children = %s")
            family_values.append(int(children))

        if street:
            family_updates.append("street = %s")
            family_values.append(street)

        if zip_code:
            family_updates.append("zip_code = %s")
            family_values.append(int(zip_code))

        if country:
            family_updates.append("country = %s")
            family_values.append(country)

        if phone_number:
            family_updates.append("phone_number = %s")
            family_values.append(phone_number)

        if email:
            family_updates.append("email = %s")
            family_values.append(email)

        if family_updates:
            query = f"""
                UPDATE families
                SET {', '.join(family_updates)}
                WHERE HEX(familyID) = %s
            """
            family_values.append(family_id)
            cursor.execute(query, tuple(family_values))

        adoptive_updates = []
        adoptive_values = []

        if num_pets_owned != "":
            adoptive_updates.append("num_pets_owned = %s")
            adoptive_values.append(int(num_pets_owned))

        if num_adults != "":
            adoptive_updates.append("num_adults = %s")
            adoptive_values.append(int(num_adults))

        if num_children != "":
            adoptive_updates.append("num_children = %s")
            adoptive_values.append(int(num_children))

        if adoptive_updates:
            cursor.execute("""
                SELECT COUNT(*)
                FROM adoptive_families
                WHERE HEX(familyID) = %s
            """, (family_id,))
            has_adoptive = cursor.fetchone()[0] > 0

            if has_adoptive:
                query = f"""
                    UPDATE adoptive_families
                    SET {', '.join(adoptive_updates)}
                    WHERE HEX(familyID) = %s
                """
                adoptive_values.append(family_id)
                cursor.execute(query, tuple(adoptive_values))
            else:
                cursor.execute("""
                    INSERT INTO adoptive_families (
                        familyID,
                        adoptive_family_ID,
                        num_pets_owned,
                        num_adults,
                        num_children
                    )
                    VALUES (UNHEX(%s), %s, %s, %s, %s)
                """, (
                    family_id,
                    uuid.uuid4().bytes,
                    int(num_pets_owned) if num_pets_owned != "" else 0,
                    int(num_adults) if num_adults != "" else 0,
                    int(num_children) if num_children != "" else 0
                ))

        if num_pets_fostered != "":
            cursor.execute("""
                SELECT COUNT(*)
                FROM foster_families
                WHERE HEX(familyID) = %s
            """, (family_id,))
            has_foster = cursor.fetchone()[0] > 0

            if has_foster:
                cursor.execute("""
                    UPDATE foster_families
                    SET num_pets_fostered = %s
                    WHERE HEX(familyID) = %s
                """, (int(num_pets_fostered), family_id))
            else:
                cursor.execute("""
                    INSERT INTO foster_families (
                        familyID,
                        foster_family_ID,
                        num_pets_fostered
                    )
                    VALUES (UNHEX(%s), %s, %s)
                """, (
                    family_id,
                    uuid.uuid4().bytes,
                    int(num_pets_fostered)
                ))

        conn.commit()
        flash("Family updated successfully.")
        return redirect(url_for("families_view", family_id=family_id))

    except Exception as e:
        if conn:
            conn.rollback()
        return f"Error updating family: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# delete families route
@app.route("/families/<family_id>/delete", methods=["POST"])
def delete_family(family_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        # delete subtype rows first
        cursor.execute("""
            DELETE FROM adoptive_families
            WHERE HEX(familyID) = %s
        """, (family_id,))

        cursor.execute("""
            DELETE FROM foster_families
            WHERE HEX(familyID) = %s
        """, (family_id,))

        # then delete the base family row
        cursor.execute("""
            DELETE FROM families
            WHERE HEX(familyID) = %s
        """, (family_id,))

        conn.commit()
        flash("Family deleted successfully.")
        return redirect(url_for("families"))

    except Exception as e:
        if conn:
            conn.rollback()
        return f"Error deleting family: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)