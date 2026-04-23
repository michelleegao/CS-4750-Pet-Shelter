from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from db.connection import getconn
import uuid
import pymysql

events_bp = Blueprint('events', __name__)

# links events search HTML page
@events_bp.route("/events")
def events():
    conn = None
    cursor = None

    try: 
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
                    SELECT
                        HEX(e.eventID) AS event_id,
                        e.street_name,
                        e.zip_code,
                        e.country,

                        DATE(e.event_date_time) AS event_date,
                        TIME(e.event_date_time) AS event_time,

                        GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR ', ') AS pet_names,

                        GROUP_CONCAT(
                            DISTINCT CONCAT(u.first_name, ' ', u.last_name)
                            ORDER BY u.first_name
                            SEPARATOR ', '
                        ) AS staff_names,

                        GROUP_CONCAT(
                            DISTINCT CONCAT(f.first_name, ' ', f.last_name)
                            ORDER BY f.first_name
                            SEPARATOR ', '
                        ) AS family_names

                    FROM adoption_event e
                    LEFT JOIN attends a ON e.eventID = a.eventID
                    LEFT JOIN adoptive_families af ON a.adoptive_family_ID = af.familyID
                    LEFT JOIN families f ON af.familyID = f.familyID
                    LEFT JOIN goes_to g ON e.eventID = g.eventID
                    LEFT JOIN pet p ON g.petID = p.petID
                    LEFT JOIN works_at wa ON e.eventID = wa.eventID
                    LEFT JOIN users u ON wa.userID = u.userID

                    GROUP BY
                        e.eventID,
                        e.street_name,
                        e.zip_code,
                        e.country,
                        e.event_date_time

                    ORDER BY e.event_date_time DESC
                """)
        
        rows = cursor.fetchall()
        events_list = []
        for row in rows:
            events_list.append({
                "event_id": row[0],
                "street_name": row[1] or "",
                "zip_code": row[2] or "",
                "country": row[3] or "",
                "event_date": row[4] or "",
                "event_time": row[5] or "",
                "pet_names": row[6] or "",
                "staff_names": row[7] or "",
                "family_names": row[8] or ""
            })

        return render_template(
            'events_search.html',
            events=events_list
        )

    except Exception as e:
        return f"Error loading events: {e}"
        
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()

# links event view for a specific event 
@events_bp.route("/events/<event_id>")
def events_view(event_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT
                HEX(e.eventID) AS event_id,
                e.street_name,
                e.zip_code,
                e.country,
                DATE(e.event_date_time) AS event_date,
                TIME(e.event_date_time) AS event_time,
                DATE_FORMAT(e.event_date_time, '%%Y-%%m-%%dT%%H:%%i') AS event_datetime_local,
                       
                GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR ', ') AS pet_names,
                GROUP_CONCAT(
                    DISTINCT CONCAT(u.first_name, ' ', u.last_name)
                    ORDER BY u.first_name
                    SEPARATOR ', '
                ) AS staff_names,
                GROUP_CONCAT(
                    DISTINCT CONCAT(f.first_name, ' ', f.last_name)
                    ORDER BY f.first_name
                    SEPARATOR ', '
                ) AS family_names
            FROM adoption_event e
            LEFT JOIN attends a ON e.eventID = a.eventID
            LEFT JOIN adoptive_families af ON a.adoptive_family_ID = af.familyID
            LEFT JOIN families f ON af.familyID = f.familyID
            LEFT JOIN goes_to g ON e.eventID = g.eventID
            LEFT JOIN pet p ON g.petID = p.petID
            LEFT JOIN works_at wa ON e.eventID = wa.eventID
            LEFT JOIN users u ON wa.userID = u.userID
            WHERE HEX(e.eventID) = %s
            GROUP BY
                e.eventID,
                e.street_name,
                e.zip_code,
                e.country,
                e.event_date_time
        """, (event_id,))
        event = cursor.fetchone()

        if not event:
            flash("Event not found.")
            return redirect(url_for("events.events"))

        # all pets
        cursor.execute("""
            SELECT HEX(petID) AS petID, name
            FROM pet
            ORDER BY name
        """)
        pets = cursor.fetchall()

        # all users
        cursor.execute("""
            SELECT HEX(userID) AS userID, first_name, last_name
            FROM users
            ORDER BY first_name, last_name
        """)
        users = cursor.fetchall()

        # all adoptive families
        cursor.execute("""
            SELECT HEX(af.familyID) AS familyID, f.first_name, f.last_name
            FROM adoptive_families af
            JOIN families f ON f.familyID = af.familyID
            ORDER BY f.first_name, f.last_name
        """)
        families = cursor.fetchall()

        # selected pets for this event
        cursor.execute("""
            SELECT HEX(petID) AS petID
            FROM goes_to
            WHERE eventID = UNHEX(%s)
        """, (event_id,))
        selected_pet_ids = [row["petID"] for row in cursor.fetchall()]

        # selected users for this event
        cursor.execute("""
            SELECT HEX(userID) AS userID
            FROM works_at
            WHERE eventID = UNHEX(%s)
        """, (event_id,))
        selected_user_ids = [row["userID"] for row in cursor.fetchall()]

        # selected families for this event
        cursor.execute("""
            SELECT HEX(adoptive_family_ID) AS familyID
            FROM attends
            WHERE eventID = UNHEX(%s)
        """, (event_id,))
        selected_family_ids = [row["familyID"] for row in cursor.fetchall()]

        return render_template(
            "events_view.html",
            event=event,
            pets=pets,
            users=users,
            families=families,
            selected_pet_ids=selected_pet_ids,
            selected_user_ids=selected_user_ids,
            selected_family_ids=selected_family_ids
        )

    except Exception as e:
        print("ERROR IN /events/<event_id>:", e)
        return f"Error loading event: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# shows edit modal for events
@events_bp.route("/events/<event_id>/edit", methods=["POST"])
def edit_event(event_id):
    conn = None
    cursor = None

    try:
        pet_ids = request.form.get("pet_ids", "")
        user_ids = request.form.get("user_ids", "")
        family_ids = request.form.get("family_ids", "")

        street = request.form.get("street")
        zip_code = request.form.get("zipCode")
        country = request.form.get("country")
        date_time = request.form.get("dateTime")
        city = request.form.get("city")
        state = request.form.get("state")

        if not street or not date_time:
            flash("Address of event and event time are required.")
            return redirect(url_for("events.events_view", event_id=event_id))

        conn = getconn()
        cursor = conn.cursor()

        if zip_code:
            cursor.execute("""
                INSERT INTO zip_codes (zip_code, city, state)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    city = VALUES(city),
                    state = VALUES(state)
            """, (zip_code, city, state))

        # update main event row
        cursor.execute("""
            UPDATE adoption_event
            SET street_name = %s,
                zip_code = %s,
                country = %s,
                event_date_time = %s
            WHERE eventID = UNHEX(%s)
        """, (street, zip_code, country, date_time, event_id))

        # clear old relations
        cursor.execute("DELETE FROM goes_to WHERE eventID = UNHEX(%s)", (event_id,))
        cursor.execute("DELETE FROM works_at WHERE eventID = UNHEX(%s)", (event_id,))
        cursor.execute("DELETE FROM attends WHERE eventID = UNHEX(%s)", (event_id,))

        # reinsert pets
        if pet_ids:
            for pet_id in pet_ids.split(","):
                pet_id = pet_id.strip()
                if pet_id:
                    cursor.execute("""
                        INSERT INTO goes_to (eventID, petID)
                        VALUES (UNHEX(%s), UNHEX(%s))
                    """, (event_id, pet_id))

        # reinsert users
        if user_ids:
            for user_id in user_ids.split(","):
                user_id = user_id.strip()
                if user_id:
                    cursor.execute("""
                        INSERT INTO works_at (eventID, userID)
                        VALUES (UNHEX(%s), UNHEX(%s))
                    """, (event_id, user_id))

        # reinsert families
        if family_ids:
            for family_id in family_ids.split(","):
                family_id = family_id.strip()
                if family_id:
                    cursor.execute("""
                        INSERT INTO attends (eventID, adoptive_family_ID)
                        VALUES (UNHEX(%s), UNHEX(%s))
                    """, (event_id, family_id))

        conn.commit()
        flash("Event updated successfully.")
        return redirect(url_for("events.events_view", event_id=event_id))

    except Exception as e:
        if conn:
            conn.rollback()
        print("ERROR EDITING EVENT:", e)
        flash(f"Error editing event: {e}")
        return redirect(url_for("events.events_view", event_id=event_id))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# links add event HTMl page
@events_bp.route("/events/add", methods=["GET", "POST"])
def events_add():
    if request.method == "GET":
        conn = None
        cursor = None
        try:
            conn = getconn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            cursor.execute("""
                SELECT HEX(petID) AS petID, name
                FROM pet
                ORDER BY name
            """)
            pets = cursor.fetchall()

            cursor.execute("""
                SELECT HEX(userID) AS userID, first_name, last_name
                FROM users
                ORDER BY first_name, last_name
            """)
            users = cursor.fetchall()

            cursor.execute("""
                SELECT HEX(af.familyID) AS familyID, f.first_name, f.last_name
                FROM adoptive_families af
                JOIN families f ON f.familyID = af.familyID
                ORDER BY f.first_name, f.last_name
            """)
            families = cursor.fetchall()

            return render_template(
                "addEvent.html",
                pets=pets,
                users=users,
                families=families
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    conn = None
    cursor = None

    try:
        pet_ids = request.form.get("pet_ids", "")
        user_ids = request.form.get("user_ids", "")
        family_ids = request.form.get("family_ids", "")

        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zipCode")
        country = request.form.get("country")
        date_time = request.form.get("dateTime")

        print("FORM DATA:", request.form)
        print("pet_ids:", pet_ids)
        print("user_ids:", user_ids)
        print("family_ids:", family_ids)
        print("street:", street)
        print("city:", city)
        print("state:", state)
        print("zip_code:", zip_code)
        print("country:", country)
        print("date_time:", date_time)

        if not street or not date_time:
            flash("Address of event and event time are required.")
            return redirect(url_for("events.events_add"))

        event_id = uuid.uuid4().bytes

        conn = getconn()
        cursor = conn.cursor()

        if zip_code:
            cursor.execute("""
                INSERT INTO zip_codes (zip_code, city, state)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    city = VALUES(city),
                    state = VALUES(state)
            """, (zip_code, city, state))

        # insert into the SAME table your events page reads from
        cursor.execute("""
            INSERT INTO adoption_event (
                eventID,
                street_name,
                zip_code,
                country,
                event_date_time,
                creation_date
            )
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (event_id, street, zip_code, country, date_time))

        if pet_ids:
            for pet_id in pet_ids.split(","):
                pet_id = pet_id.strip()
                if pet_id:
                    print("inserting pet_id:", pet_id)
                    cursor.execute("""
                        INSERT INTO goes_to (eventID, petID)
                        VALUES (%s, UNHEX(%s))
                    """, (event_id, pet_id))

        if user_ids:
            for user_id in user_ids.split(","):
                user_id = user_id.strip()
                if user_id:
                    cursor.execute("""
                        INSERT INTO works_at (eventID, userID)
                        VALUES (%s, UNHEX(%s))
                    """, (event_id, user_id))

        if family_ids:
            for family_id in family_ids.split(","):
                family_id = family_id.strip()
                if family_id:
                    cursor.execute("""
                        INSERT INTO attends (eventID, adoptive_family_ID)
                        VALUES (%s, UNHEX(%s))
                    """, (event_id, family_id))

        conn.commit()
        flash("Event added successfully.")
        return redirect(url_for("events.events"))

    except Exception as e:
        if conn:
            conn.rollback()
        print("ERROR ADDING EVENT:", e)
        flash(f"Error adding event: {e}")
        return redirect(url_for("events.events_add"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@events_bp.route("/events/<event_id>/delete", methods=["POST"])
def delete_event(event_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        # Delete child table records first because of foreign keys
        cursor.execute("DELETE FROM goes_to WHERE eventID = UNHEX(%s)", (event_id,))
        cursor.execute("DELETE FROM works_at WHERE eventID = UNHEX(%s)", (event_id,))
        cursor.execute("DELETE FROM attends WHERE eventID = UNHEX(%s)", (event_id,))

        # Delete main event
        cursor.execute("DELETE FROM adoption_event WHERE eventID = UNHEX(%s)", (event_id,))

        conn.commit()
        flash("Event deleted successfully.")
        return redirect(url_for("events.events"))

    except Exception as e:
        if conn:
            conn.rollback()
        print("ERROR DELETING EVENT:", e)
        flash(f"Error deleting event: {e}")
        return redirect(url_for("events.events_view", event_id=event_id))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()