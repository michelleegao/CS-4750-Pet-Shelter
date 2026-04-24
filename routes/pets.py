from db.connection import getconn
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from google.cloud import storage
from datetime import timedelta, datetime, timezone
import uuid

pet_blueprint = Blueprint('pet', __name__)

bucket_name = "pets-database"

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

# links pets view HTML page
@pet_blueprint.route("/pets_view")
def pets_view():
    conn = getconn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pet")
    pets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("pets_view.html", pets=pets)

@pet_blueprint.route("/pets_search", methods=["GET"])
def get_all_pets():
    if request.method == "GET":
        query = "SELECT BIN_TO_UUID(petID) as petIDString, species, age, color, breed, siblings, weight, image_url, name FROM pet WHERE petID NOT IN (SELECT petID FROM previous_pet)"
        previous_query = "SELECT BIN_TO_UUID(petID) as petIDString, species, age, color, breed, siblings, weight, image_url, name FROM pet NATURAL JOIN previous_pet"
        params = ()
        breed_query = "SELECT DISTINCT breed FROM pet"
        breed_list = run_query(breed_query, fetch=True)

        query_param = request.args.get("query", "").strip()
        if query_param:
            search_term = f"%{query_param}%"
            query = """SELECT BIN_TO_UUID(petID) as petIDString, species, age, color, breed, siblings, weight, image_url, name FROM pet 
            WHERE species LIKE %s OR age LIKE %s OR color LIKE %s OR breed LIKE %s OR name like %s AND petID NOT IN (SELECT petID FROM previous_pet)"""
            previous_query = """SELECT BIN_TO_UUID(petID) as petIDString, species, age, color, breed, siblings, weight, image_url, name FROM pet NATURAL JOIN previous_pet
            WHERE species LIKE %s OR age LIKE %s OR color LIKE %s OR breed LIKE %s OR name like %s"""
            params = (search_term, search_term, search_term, search_term, search_term)

        get_all_pets = run_query(query, params, fetch=True)
        get_previous_pets = run_query(previous_query, params, fetch=True)

        print("ARGS:", request.args)
        return render_template('/pets_search.html', pets=get_all_pets, previous_pets=get_previous_pets, breed=breed_list)
    
    
@pet_blueprint.route("/pet/<pet_id>", methods=["GET", "POST"])
def pet_detail(pet_id):
    if request.method == "GET":
        pet_query = "SELECT *, BIN_TO_UUID(petID) AS petIDString FROM pet WHERE petID = UUID_TO_BIN(%s)"
        pet = run_query(pet_query, (pet_id,), fetch=True)[0]
        timestamp = pet[8]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        days_in_shelter = (datetime.now(timezone.utc) - timestamp).days

        if (pet[6] is True):
            fixed = "yes"
        else:
            fixed = "no"
        
        if (pet[15] is True):
            siblings = "yes"
        else:
            siblings = "no"

        if (pet[17] is True):
            special_needs = "yes"
        else:
            special_needs = "no"

        ## find foster family ID if exists
        if (pet[18] is not None):
            fam_query = "SELECT BIN_TO_UUID(familyID), last_name, phone_number, email FROM families WHERE familyID=%s"
            foster_family = run_query(fam_query, (pet[18],), fetch=True)[0]
            familyID = foster_family[0]
            family_name = foster_family[1] + " Family"
            family_phone = foster_family[2]
            family_email = foster_family[3]
        else:
            familyID = "NA"
            family_name = "NA"
            family_phone = "NA"
            family_email = "NA"

        get_fosters_query = "SELECT BIN_TO_UUID(familyID), first_name, last_name FROM families NATURAL JOIN foster_families"
        get_fosters = run_query(get_fosters_query, fetch=True)

        get_adoptives_query = "SELECT BIN_TO_UUID(familyID), first_name, last_name FROM families NATURAL JOIN adoptive_families"
        get_adoptives = run_query(get_adoptives_query, fetch=True)

        get_previous_pets_query = "SELECT BIN_TO_UUID(petID), reason_for_deletion, BIN_TO_UUID(adoptive_familyID), date_of_deletion FROM previous_pet WHERE petID = UUID_TO_BIN(%s)"
        get_previous_pets = run_query(get_previous_pets_query, (pet_id,), fetch=True)

        if get_previous_pets==():
            adoptive_ID = None
            reason_for_deletion = None
            date_of_deletion = None
            deleted_from_database = False
        else:
            adoptive_ID = get_previous_pets[0][2]
            reason_for_deletion = get_previous_pets[0][1]
            date_of_deletion = get_previous_pets[0][3]
            deleted_from_database = True

        pet_data = {
            "petID": pet[20],
            "species" : pet[1],
            "age" : pet[2],
            "name" : pet[3].title(),
            "color" : pet[4],
            "description" : pet[5],
            "fixed" : fixed,
            "adoption_status" : pet[7],
            "days_in_shelter" : days_in_shelter,
            "breed" : pet[13].title(),
            "weight" : pet[14],
            "siblings" : siblings,
            "sex" : pet[16],
            "special_needs" : special_needs,
            "current_location" : pet[12],
            "foster_ID" : familyID,
            "foster_name" : family_name,
            "foster_phone" : family_phone,
            "foster_email" : family_email,
            "image_url" : pet[19],
            "adoptive_family" : adoptive_ID,
            "deleted" : deleted_from_database,
            "deletion_reason" : reason_for_deletion,
            "deletion_date" : date_of_deletion
        }

        return render_template("/pets_view.html", pets=pet_data, fosters=get_fosters, adoptives=get_adoptives)
    elif request.method=="POST":
        action = request.form.get("action")
        if action == "update":
            pet_name = request.form.get("pet_name").lower()
            pet_age = request.form.get("pet_age")
            pet_description = request.form.get("pet_description").lower()
            if (request.form.get("pet_fixed") == "yes"):
                pet_fixed = True
            else:
                pet_fixed = False
            pet_curr_location = request.form.get("pet_curr_location")
            if (pet_curr_location=="Foster Home"):
                foster_id = request.form.get("foster_id")
            else:
                foster_id = None
            pet_breed = request.form.get("pet_breed").lower()
            pet_weight = request.form.get("pet_weight")
            if (request.form.get("pet_special_needs" == "yes")):
                pet_special_needs = True
            else:
                pet_special_needs = False
            pet_photo = request.files.get("pet_photo")
            pet_adoption_status = request.form.get("pet_adoption")
            pet_adoptive_family = request.form.get("pet_adoption_family")

            if pet_photo is None:
                update_pet_query = "UPDATE pet SET adoption_status=%s, name=%s, age=%s, description=%s, current_location=%s, foster_familyID=UUID_TO_BIN(%s), spayed_or_neutered=%s, breed=%s, weight=%s, special_needs=%s WHERE petID=UUID_TO_BIN(%s)"
                params = (pet_adoption_status, pet_name, pet_age, pet_description, pet_curr_location, foster_id, pet_fixed, pet_breed, pet_weight, pet_special_needs, pet_id,)
                run_query(update_pet_query, params, fetch=False)
                if pet_adoption_status=="Adopted":
                    previous_pet_query = "INSERT IGNORE INTO previous_pet (petID, reason_for_deletion, date_of_deletion, adoptive_familyID) VALUES (UUID_TO_BIN(%s), %s, NOW(), UUID_TO_BIN(%s))" ## come back here 
                    previous_pet_params = (pet_id, pet_adoption_status, pet_adoptive_family)
                    run_query(previous_pet_query, previous_pet_params, fetch=False)
            else:
                ## Uploading Pet Photo to Google Cloud
                filename = f"{uuid.uuid4()}.jpg"

                client = storage.Client()
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(filename)

                blob.upload_from_file(pet_photo)

                photo_url = blob.public_url

                update_pet_query = "UPDATE pet SET adoption_status=%s, name=%s, age=%s, description=%s, current_location=%s, foster_familyID=UUID_TO_BIN(%s), spayed_or_neutered=%s, breed=%s, weight=%s, special_needs=%s, image_url=%s WHERE petID=UUID_TO_BIN(%s)"
                params = (pet_adoption_status, pet_name, pet_age, pet_description, pet_curr_location, foster_id, pet_fixed, pet_breed, pet_weight, pet_special_needs, photo_url, pet_id,)
                run_query(update_pet_query, params, fetch=False)
                if pet_adoption_status=="Adopted":
                    previous_pet_query = "INSERT IGNORE INTO previous_pet (petID, reason_for_deletion, date_of_deletion, adoptive_familyId) VALUES (UUID_TO_BIN(%s), %s, NOW(), UUID_TO_BIN(%s))" ## come back here 
                    previous_pet_params = (pet_id, pet_adoption_status, pet_adoptive_family)
                    run_query(previous_pet_query, previous_pet_params, fetch=False)
            return redirect(url_for("pet.pet_detail", pet_id=pet_id))
        elif action == "delete":
            delete_description = request.form.get("pet_deletion_reason")
            adoptive_family_id = request.form.get("pet_adoption_family")
            adoption_status = request.form.get("pet_adoption")
            delete_pet_query = "INSERT IGNORE INTO previous_pet (petID, reason_for_deletion, date_of_deletion, adoptive_familyID) VALUES (UUID_TO_BIN(%s), %s, NOW(), UUID_TO_BIN(%s))"
            delete_pet_params = (pet_id, delete_description, adoptive_family_id,)
            run_query(delete_pet_query, delete_pet_params, fetch=False)
            if adoption_status != "":
                adoption_status_change_query = "UPDATE pet SET adoption_status=%s WHERE petID=UUID_TO_BIN(%s)"
                adoption_status_change_params = (adoption_status, pet_id)
                run_query(adoption_status_change_query, adoption_status_change_params, fetch=False)
            return redirect(url_for("pet.pet_detail", pet_id=pet_id))
            
            





        
## come back to this! 


@pet_blueprint.route("/addpet", methods=["GET", "POST"])
def add_pet():
    if request.method == "GET":
        ## get all pets for the sibling drop-down
        get_pets_query = "SELECT BIN_TO_UUID(petID), name, species, breed FROM pet"
        get_pets = run_query(get_pets_query, fetch=True)
        get_fosters_query = "SELECT BIN_TO_UUID(familyID), first_name, last_name FROM families NATURAL JOIN foster_families"
        get_fosters = run_query(get_fosters_query, fetch=True)
        state = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
        "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
        "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
        "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
        ]
        return render_template("/addpet.html", pets=get_pets, fosters=get_fosters, states=state)
    
    pet_name = request.form.get("pet_name").lower()
    pet_species = request.form.get("species_name").lower()
    pet_age = request.form.get("pet_age")
    pet_color = request.form.get("pet_color").lower()
    pet_description = request.form.get("pet_description").lower()
    if (request.form.get("pet_fixed") == "yes"):
        pet_fixed = True
    else:
        pet_fixed = False
    ## pet_adoption_status = request.form.get("pet_adoption_status")
    pet_street = request.form.get("pet_street").title()
    pet_city = request.form.get("pet_city").title()
    pet_state = request.form.get("pet_state")
    pet_zip = request.form.get("pet_zip")
    pet_country = request.form.get("pet_country").title()
    pet_curr_location = request.form.get("pet_curr_location")
    if (pet_curr_location=="Foster Home"):
        foster_id = request.form.get("foster_id")
    else:
        foster_id = None

    pet_breed = request.form.get("pet_breed").lower()
    pet_weight = request.form.get("pet_weight")
    if (request.form.get("pet_has_sibling")=="yes"):
        pet_has_sibling=True
    else:
        pet_has_sibling=False
    pet_sex = request.form.get("pet_sex")
    if (request.form.get("pet_special_needs" == "yes")):
        pet_special_needs = True
    else:
        pet_special_needs = False
    pet_photo = request.files.get("pet_photo")
    pet_id = uuid.uuid4().bytes
    
    ## Uploading Pet Photo to Google Cloud
    filename = f"{uuid.uuid4()}.jpg"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.upload_from_file(pet_photo)

    photo_url = blob.public_url

    query = "INSERT INTO pet (petID, species, age, name, color, description, spayed_or_neutered, adoption_status, creation_date, country, street_name, zip_code, current_location, breed, weight, siblings, sex, special_needs, foster_familyID, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, UUID_TO_BIN(%s), %s)"
    params = (pet_id, pet_species, pet_age, pet_name, pet_color, pet_description, pet_fixed, "Not Yet Adopted", pet_country, pet_street, pet_zip, pet_curr_location, pet_breed, pet_weight, pet_has_sibling, pet_sex, pet_special_needs, foster_id, photo_url)
    run_query(query, params, fetch=False)

    query = "INSERT IGNORE INTO zip_codes (zip_code, city, state) VALUES (%s, %s, %s)"
    params = (pet_zip, pet_city, pet_state)
    run_query(query, params, fetch=False)

    if pet_has_sibling is True:
        sibling_id = request.form.get("sibling_id")
        query = "INSERT IGNORE INTO is_a_sibling_of (petID1, petID2) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))"
        params = (pet_id, sibling_id)
        run_query(query, params, fetch=False)
    
    return redirect(url_for("pet.get_all_pets"))

@pet_blueprint.route("/delete_pet/<pet_id>", methods=["POST"])
def delete_pet(pet_id):
    conn = getconn()
    cursor = conn.cursor()

    try:
        params = (pet_id, )

        cursor.execute("DELETE FROM previous_pet WHERE petID = UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM is_a_sibling_of WHERE petID1 = UUID_TO_BIN(%s) OR petID2 = UUID_TO_BIN(%s)",
                       (pet_id, pet_id))
        cursor.execute("DELETE FROM appointments WHERE petID = UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM goes_to WHERE petID=UUID_TO_BIN(%s)", params)
        cursor.execute("DELETE FROM pet WHERE petID = UUID_TO_BIN(%s)", params)
        
        conn.commit()
        
        print("Deleting Pet: ", pet_id)
        return "", 204
    except Exception as e:
        conn.rollback()
        print("Delete Failed: ", e)
        return "Error deleting pet", 500
    finally:
        cursor.close()
        conn.close()