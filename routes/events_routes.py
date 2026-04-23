from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from db.connection import getconn
import uuid

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
                    LEFT JOIN adoptive_families af ON a.adoptive_family_ID = af.adoptive_family_ID
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
