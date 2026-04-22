from db.connection import getconn
from flask import Blueprint, request, jsonify, render_template
from google.cloud import storage
from datetime import timedelta
import uuid

pet_blueprint = Blueprint('pet', __name__)

bucket_name = "pets-database"
## from flask import

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

@pet_blueprint.route("/pets_search")
def pets():
    return render_template('/pets_search.html')

# links pets view HTML page
@pet_blueprint.route("/pets_view")
def pets_view():
    return render_template('/pets_view.html')

@pet_blueprint.route("/pets_search", methods=["GET"])
def get_all_pets():
    query = "SELECT * FROM pet"
    return run_query(query, fetch=True)

@pet_blueprint.route("/addpet", methods=["GET", "POST"])
def add_pet():
    if request.method == "GET":
        return render_template("/addpet.html")
    
    pet_name = request.form.get("pet_name")
    pet_species = request.form.get("species_name")
    pet_age = request.form.get("pet_age")
    pet_color = request.form.get("pet_color")
    pet_description = request.form.get("pet_description")
    pet_fixed = request.form.get("pet_fixed")
    pet_adoption_status = request.form.get("pet_adoption_status")
    pet_street = request.form.get("pet_street")
    pet_city = request.form.get("pet_city")
    pet_state = request.form.get("pet_state")
    pet_zip = request.form.get("pet_zip")
    pet_country = request.form.get("pet_country")
    pet_curr_location = request.form.get("pet_curr_location")
    ## need to add in the connection between foster family and pet
    pet_breed = request.form.get("pet_breed")
    pet_weight = request.form.get("pet_weight")
    pet_has_sibling = request.form.get("pet_has_sibling")
    pet_sex = request.form.get("pet_sex")
    pet_special_needs = request.form.get("pet_special_needs")
    pet_photo = request.files.get("pet_photo")
    
    ## Uploading Pet Photo to Google Cloud
    filename = f"{uuid.uuid4()}.jpg"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.upload_from_file(pet_photo)

    photo_url = blob.public_url

    conn = getconn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pet (petID, species, age, name, color, description, spayed_or_neutered, adoption_status, creation_date, country, street_name, zip_code, current_location, breed, weight, siblings, sex, special_needs, foster_familyID, image_url) "
        "VALUES (UUID_TO_BIN(UUID()), %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s)",
        (pet_species, pet_age, pet_name, pet_color, pet_description, pet_fixed, pet_adoption_status, pet_country, pet_street, pet_zip, pet_curr_location, pet_breed, pet_weight, pet_has_sibling, pet_sex, pet_special_needs, photo_url)
    )
    cursor.execute(
        "INSERT IGNORE INTO zip_codes (zip_code, city, state) VALUES (%s, %s, %s)",
        (pet_zip, pet_city, pet_state)
    )

    conn.commit()
    cursor.close()
    conn.close()
    
    


"""@pet_blueprint.route("/addpet", methods=["POST"])
def add_pet():

    pet_name = request.form.get("pet_name")
    pet_species = request.form.get("species_name")
    pet_age = request.form.get("pet_age")
    pet_color = request.form.get("pet_color")
    pet_description = request.form.get("pet_description")
    pet_fixed = request.form.get("pet_fixed")
    pet_adoption_status = request.form.get("pet_adoption_status")
    pet_street = request.form.get("pet_street")
    pet_city = request.form.get("pet_city")
    pet_state = request.form.get("pet_state")
    pet_zip = request.form.get("pet_zip")
    pet_country = request.form.get("pet_country")
    pet_curr_location = request.form.get("pet_curr_location")
    ## need to add in the connection between foster family and pet
    pet_breed = request.form.get("pet_breed")
    pet_weight = request.form.get("pet_weight")
    pet_has_sibling = request.form.get("pet_has_sibling")
    pet_sex = request.form.get("pet_sex")
    pet_special_needs = request.form.get("pet_special_needs")
    pet_photo = request.files.get("pet_photo")
    
    ## Uploading Pet Photo to Google Cloud
    filename = f"{uuid.uuid4()}.jpg"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.upload_from_file(pet_photo)
    blob.make_public()

    photo_url = blob.public_url

    conn = getconn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pet (petID, species, age, name, color, description, spayed_or_neutered, adoption_status, creation_date, country, street_name, zip_code, current_location, breed, weight, siblings, sex, special_needs, foster_familyID, image_url) "
        "VALUES (UUID_TO_BIN(UUID()), %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s)",
        (pet_species, pet_age, pet_name, pet_color, pet_description, pet_fixed, pet_adoption_status, pet_country, pet_street, pet_zip, pet_curr_location, pet_breed, pet_weight, pet_has_sibling, pet_sex, pet_special_needs, photo_url)
    )
    cursor.execute(
        "INSERT IGNORE INTO zip_codes (zip_code, city, state) VALUES (%s, %s, %s)",
        (pet_zip, pet_city, pet_state)
    )

    conn.commit()
    cursor.close()
    conn.close()"""

    

## filtering -- implement later
"""def filter_pets(species=None, min_age=None, max_age=None):
    query = "SELECT * FROM pets WHERE 1=1"
    params = []

    if species:
        query += " AND species = %s"
        params.append(species)

    if min_age:
        query += " AND age >= %s"
        params.append(min_age)

    if max_age:
        query += " AND age <= %s"
        params.append(max_age)

    return run_query(query, tuple(params), fetch_all=True)"""