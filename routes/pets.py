from db.connection import getconn
from flask import Blueprint, request, jsonify, render_template
from google.cloud import storage
from datetime import timedelta
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
    return render_template('/pets_view.html')

@pet_blueprint.route("/pets_search", methods=["GET"])
def get_all_pets():
    if request.method == "GET":
        query = "SELECT BIN_TO_UUID(petID) as petIDString, species, age, color, breed, siblings, weight, image_url, name FROM pet"
        get_all_pets = run_query(query, fetch=True)
        # print(get_all_pets[0][7])
        return render_template('/pets_search.html', pets=get_all_pets)
    
@pet_blueprint.route("/pet/<pet_id>")
def pet_detail(pet_id):
    query = "SELECT * FROM pet WHERE petID = UUID_TO_BIN(%s)"
    pet = run_query(query, (pet_id,), fetch=True)[0]
    return render_template("/pets_view.html", pets=pet)
## come back to this! 


@pet_blueprint.route("/addpet", methods=["GET", "POST"])
def add_pet():
    if request.method == "GET":
        ## get all pets for the sibling drop-down
        get_pets_query = "SELECT petID, name, species, breed FROM pet"
        get_pets = run_query(get_pets_query, fetch=True)
        get_fosters_query = "SELECT familyID, first_name, last_name FROM families NATURAL JOIN foster_families"
        get_fosters = run_query(get_fosters_query, fetch=True)
        return render_template("/addpet.html", pets=get_pets, fosters=get_fosters)
    
    pet_name = request.form.get("pet_name").lower()
    pet_species = request.form.get("species_name").lower()
    pet_age = request.form.get("pet_age")
    pet_color = request.form.get("pet_color").lower()
    pet_description = request.form.get("pet_description").lower()
    pet_fixed = request.form.get("pet_fixed")
    ## pet_adoption_status = request.form.get("pet_adoption_status")
    pet_street = request.form.get("pet_street").lower()
    pet_city = request.form.get("pet_city")
    pet_state = request.form.get("pet_state")
    pet_zip = request.form.get("pet_zip")
    pet_country = request.form.get("pet_country")
    pet_curr_location = request.form.get("pet_curr_location")
    if pet_curr_location=="Foster":
        foster_id = request.form.get("foster_id")
    else:
        foster_id = None

    pet_breed = request.form.get("pet_breed")
    pet_weight = request.form.get("pet_weight")
    if (request.form.get("pet_has_sibling")=="yes"):
        pet_has_sibling=True
    else:
        pet_has_sibling=False
    pet_sex = request.form.get("pet_sex")
    pet_special_needs = request.form.get("pet_special_needs")
    pet_photo = request.files.get("pet_photo")
    pet_id = uuid.uuid4().bytes
    
    ## Uploading Pet Photo to Google Cloud
    filename = f"{uuid.uuid4()}.jpg"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.upload_from_file(pet_photo)

    photo_url = blob.public_url

    query = "INSERT INTO pet (petID, species, age, name, color, description, spayed_or_neutered, adoption_status, creation_date, country, street_name, zip_code, current_location, breed, weight, siblings, sex, special_needs, foster_familyID, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    params = (pet_id, pet_species, pet_age, pet_name, pet_color, pet_description, pet_fixed, "Not Yet Adopted", pet_country, pet_street, pet_zip, pet_curr_location, pet_breed, pet_weight, pet_has_sibling, pet_sex, pet_special_needs, foster_id, photo_url)
    run_query(query, params, fetch=False)

    query = "INSERT IGNORE INTO zip_codes (zip_codes, city, state) VALUES (%s, %s, %s)"
    params = (pet_zip, pet_city, pet_state)
    run_query(query, params, fetch=False)

    if pet_has_sibling is True:
        sibling_id = request.form.get("sibling_id")
        query = "INSERT IGNORE INTO is_a_sibling_of (petID1, petID2) VALUES (%s, %s)"
        params = (pet_id, sibling_id)
        run_query(query, params, fetch=False)

    

    

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