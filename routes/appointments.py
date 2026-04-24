from flask import Blueprint, render_template, request, redirect, url_for
from db.connection import getconn
import uuid
from datetime import datetime
from flask import session

appointments_bp = Blueprint('appointments', __name__)

# VIEW ALL APPOINTMENTS
@appointments_bp.route("/appointments")
def appointments_view():
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                HEX(appointmentID),
                HEX(petID),
                HEX(userID),
                appointment_date_time,
                appointment_reason,
                cost,
                notes
            FROM appointments
            ORDER BY appointment_date_time DESC
        """)

        rows = cursor.fetchall()

        appointments = []
        for r in rows:
            appointments.append({
                "appointment_id": r[0],
                "pet_id": r[1],
                "user_id": r[2],
                "datetime": r[3],
                "reason": r[4],
                "cost": r[5],
                "notes": r[6]
            })

        return render_template("appointment.html", appointments=appointments)

    except Exception as e:
        return f"Error loading appointments: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# VIEW ONE APPOINTMENT
@appointments_bp.route("/appointments/<appointment_id>")
def appointment_detail(appointment_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                HEX(appointmentID),
                HEX(petID),
                HEX(userID),
                appointment_date_time,
                appointment_reason,
                cost,
                notes
            FROM appointments
            WHERE appointmentID = UNHEX(%s)
        """, (appointment_id,))

        row = cursor.fetchone()

        if not row:
            return "Appointment not found", 404

        appointment = {
            "appointment_id": row[0],
            "pet_id": row[1],
            "user_id": row[2],
            "datetime": row[3],
            "reason": row[4],
            "cost": row[5],
            "notes": row[6]
        }

        return render_template("appointment_detail.html", appointment=appointment)

    except Exception as e:
        return f"Error loading appointment: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ADD PAGE
@appointments_bp.route("/appointments/add")
def add_appointment():
    return render_template("addappointment.html")


# CREATE APPOINTMENT (POST)
@appointments_bp.route("/appointments/add", methods=["POST"])
def create_appointment():
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        appointment_id = uuid.uuid4().hex
        pet_id = request.form["pet_id"]
        user_id = request.form["user_id"]
        datetime_val = request.form["datetime"]
        reason = request.form["reason"]
        cost = request.form["cost"]
        notes = request.form["notes"]
        creationDateTime = datetime.utcnow()

        cursor.execute("""
            INSERT INTO appointments (
                appointmentID,
                appointment_date_time,
                appointment_reason,
                cost,
                notes,
                creation_date,
                petID,
                userID
            )
            VALUES (
                UNHEX(%s),
                %s,
                %s,
                %s,
                %s,
                %s,
                UNHEX(%s),
                UNHEX(%s)
            )
        """, (appointment_id, datetime_val, reason, cost, notes, creationDateTime, pet_id, user_id))

        conn.commit()

        return redirect(url_for("appointments.appointments_view"))

    except Exception as e:
        return f"Insert failed: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# EDIT PAGE
@appointments_bp.route("/appointments/edit/<appointment_id>")
def edit_appointment_page(appointment_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                HEX(appointmentID),
                HEX(petID),
                HEX(userID),
                appointment_date_time,
                appointment_reason,
                cost,
                notes
            FROM appointments
            WHERE appointmentID = UNHEX(%s)
        """, (appointment_id,))

        row = cursor.fetchone()

        if not row:
            return "Appointment not found", 404

        appointment = {
            "appointment_id": row[0],
            "pet_id": row[1],
            "user_id": row[2],
            "datetime": row[3],
            "reason": row[4],
            "cost": row[5],
            "notes": row[6]
        }

        return render_template("editappointment.html", appointment=appointment)

    except Exception as e:
        return f"Error loading edit page: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# UPDATE APPOINTMENT
@appointments_bp.route("/appointments/edit/<appointment_id>", methods=["POST"])
def update_appointment(appointment_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        pet_id = request.form["pet_id"]
        user_id = request.form["user_id"]
        datetime_val = request.form["datetime"]
        reason = request.form["reason"]
        cost = request.form["cost"]
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE appointments
            SET
                petID = UNHEX(%s),
                userID = UNHEX(%s),
                appointment_date_time = %s,
                appointment_reason = %s,
                cost = %s,
                notes = %s
            WHERE appointmentID = UNHEX(%s)
        """, (pet_id, user_id, datetime_val, reason, cost, notes, appointment_id))

        conn.commit()

        return redirect(url_for("appointments.appointments_view"))

    except Exception as e:
        return f"Update failed: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# DELETE APPOINTMENT
@appointments_bp.route("/appointments/delete/<appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    conn = None
    cursor = None

    try:
        conn = getconn()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM appointments
            WHERE appointmentID = UNHEX(%s)
        """, (appointment_id,))

        conn.commit()

        return "OK"

    except Exception as e:
        return f"Delete failed: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()