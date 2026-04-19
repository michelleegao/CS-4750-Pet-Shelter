document.getElementById("add-pet-form").addEventListener("submit", async  (e) =>{
    e.preventDefault();

    const siblingSelected = document.querySelector('input[name="sibling"]:checked');
    const siblingValueInput = document.getElementById("pet-popup-value");

    // Only enforce requirement if "yes"
    if (siblingSelected && siblingSelected.value === "yes") {
        if (!siblingValueInput.value) {
            e.preventDefault(); // stop form submission
            alert("Please select a sibling pet.");
            openModal('pet-modal');
        }
    }

    const form = document.getElementById("add-pet-form");
    const pet_photo = document.getElementById("pet-photo").files[0];
    const species = document.querySelector('input[name="species"]:checked')?.value;
    const fixed = document.querySelector('input[name="spayed-neutered"]:checked')?.value;
    const sex = document.querySelector('input[name="sex"]:checked')?.value;
    const cur_location = document.querySelector('input[name="cur-location"]:checked')?.value;
    const sibling = document.querySelector('input[name="sibling"]:checked')?.value;

    const formData = new FormData();
    formData.append("pet_name", document.getElementById("name").value)
    formData.append("species_name", species)
    formData.append("pet_age", document.getElementById("age").value)
    formData.append("pet_color", document.getElementById("color").value)
    formData.append("pet_description", document.getElementById("description").value)
    formData.append("pet_fixed", fixed)
    formData.append("pet_adoption_status", "Not yet adopted")
    formData.append("pet_street", document.getElementById("location-street").value)
    formData.append("pet_city", document.getElementById("location-city").value)
    formData.append("pet_state", document.getElementById("location-state").value)
    formData.append("pet_zip", document.getElementById("location-zip").value)
    formData.append("pet_country", document.getElementById("location-country").value)
    formData.append("pet_curr_location", cur_location)
    formData.append("pet_breed", document.getElementById("breed").value)
    formData.append("pet_weight", document.getElementById("weight").value)
    formData.append("pet_has_sibling", sibling)
    formData.append("pet_sex", sex)
    formData.append("pet_special_needs", document.getElementById("special-needs").value)
    formData.append("pet_photo", pet_photo)

    const response = await fetch("/addpet", {
        method: "POST",
        body: formData
    })

    const text = await response.text();
    console.log("RAW RESPONSE:", text);
    // const data = await response.json();
    //console.log(data);
})