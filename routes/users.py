from db.connection import getconn
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from google.cloud import storage
from datetime import timedelta, datetime, timezone
import uuid
import json

users_blueprint = Blueprint('users', __name__)

def run_query(query, params=None, fetch=False):
    conn = getconn()
    cursor = conn.cursor()

    cursor.execute(query, params or ())

    result = None
    if fetch:
        result = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return result

@users_blueprint.route("/users_search", methods=["GET"])
def get_all_users():
    if request.method == "GET":
        query = """SELECT BIN_TO_UUID(u.userID) AS userIDString, u.first_name, u.last_name, u.email, u.phone_number, u.role, m.managerID 
        FROM users u LEFT JOIN managers m ON u.userID=m.userID"""
        params = ()

        query_param = request.args.get("query", "").strip()
        if query_param:
            search_term = f"%{query_param}%"
            query = """SELECT BIN_TO_UUID(u.userID) AS userIDString, 
            u.first_name, u.last_name, u.email, u.phone_number, u.role, m.managerID 
            FROM users u LEFT JOIN managers m ON u.userID=m.userID 
            WHERE u.first_name LIKE %s OR u.last_name LIKE %s OR u.email LIKE %s OR u.role LIKE %s"""
            params = (search_term, search_term, search_term, search_term)
            if search_term.lower() == "manager":
                query = query + " OR m.manager NOT NULL" 
                
        get_all_users = run_query(query, params, fetch=True)

        print("ARGS:", request.args)
        return render_template('/user_search.html', users=get_all_users)

@users_blueprint.route("/users/<user_id>", methods=["GET", "POST"])
def users_view(user_id):
    if request.method=="GET":
        user_query = """SELECT BIN_TO_UUID(u.userID) AS userIDString, 
            u.first_name, u.last_name, u.email, u.phone_number, u.role, m.managerID 
            FROM users u LEFT JOIN managers m ON u.userID=m.userID  WHERE u.userID = UUID_TO_BIN(%s)"""
        user = run_query(user_query, (user_id,), fetch=True)[0]
        if user[6] is not None:
            users_managed_query = """SELECT BIN_TO_UUID(m.userID as managed_id, u.first_name as first, u.last_name as last FROM
            users u LEFT JOIN manages m ON m.userID = u.userID WHERE m.managerID = UUID_TO_BIN(%s)"""
            managed_users = run_query(users_managed_query, (user_id), fetch=True)
            managed_names  = tuple(f"{first} {last}" for first, last in managed_users)
            managed_ids = tuple(f"{managed_id}" for managed_id in managed_users)
        else:
            managed_names = ()
            managed_users = []
            managed_ids = None
        all_otherusers_query = """SELECT BIN_TO_UUID(u.userID) AS userIDString, 
            u.first_name, u.last_name, u.email, u.phone_number, u.role, m.managerID 
            FROM users u LEFT JOIN managers m ON u.userID=m.userID WHERE u.userID <> UUID_TO_BIN(%s)"""
        all_other_users = run_query(all_otherusers_query, (user_id), fetch=True)
        
        user_data = {
            "userID" : user[0],
            "userFirst" : user[1],
            "userLast" : user[2],
            "userEmail" : user[3],
            "userPhone" : user[4],
            "userRole" : user[5],
            "userManager" : user[6],
            "managedNames" : managed_names,
            "managedUsers" : managed_users,
            "managedIds" : managed_ids
        }

        return render_template("/user_view.html", user=user_data, all_users = all_other_users)
    if request.method=="POST":
        action = request.form.get("action")
        if action == "update":
            user_role = request.form.get("user_role").lower()
            manager_status = request.form.get("manager_status")
            managed_employees = json.loads(request.form.get("managed_employees"))

            print(uuid.UUID(user_id))

            conn = getconn()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET role=%s WHERE UUID_TO_BIN(%s)=userID",
                               (user_role, user_id))
                
                if (manager_status=="yes"):
                    cursor.execute("INSERT IGNORE INTO managers (userID, managerID) VALUES (%s, UUID_TO_BIN(UUID()))",
                                   (user_id,))
                    for employee in managed_employees:
                        cursor.execute("INSERT IGNORE INTO manages (managerID, userID) VALUES (%s, %s)",
                                       (user_id, employee))
                        
                conn.commit()
                        
            except Exception as e:
                conn.rollback()
                print("Delete Failed: ", e)
                return "Error editing user", 500
            
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for("users.get_all_users"))


@users_blueprint.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    conn = getconn()
    cursor = conn.cursor()

    try:
        params = (user_id, )

        cursor.execute("DELETE FROM works_at WHERE userID=UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM appointments WHERE userID=UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM manages WHERE managerID=UUID_TO_BIN(%s) OR userID=UUID_TO_BIN(%s)", (user_id, user_id, ))
        cursor.execute("DELETE FROM managers WHERE userID=UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM users WHERE userID=UUID_TO_BIN(%s)", params)
        conn.commit()
        
        print("Deleting User: ", user_id)
        return "", 204
    except Exception as e:
        conn.rollback()
        print("Delete Failed: ", e)
        return "Error deleting user", 500
    finally:
        cursor.close()
        conn.close()