// Clear form on Load:

window.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[type="radio"]').forEach(r => {
    r.checked = false;
  });

});
  
  
const siblingRadios = document.querySelectorAll('input[name="sibling"]');
const fosterRadios = document.querySelectorAll('input[name="cur-location"]');
const siblingSection = document.getElementById('sibling-section');
const locationSection = document.getElementById('location-section');
  
function openModal(id){
  document.getElementById(id).style.display = "block";
}
  
function closeModal(modal_name) {
  document.getElementById(modal_name).style.display = "none";
}

function cancelModal(id, modal_name){
  document.getElementById(id).value = "";
  closeModal(modal_name);
}
  
function saveModalValue(id, modal_name) {
  const value = document.getElementById(id).value;
  document.getElementById(id).value = value;
  closeModal(modal_name);
}

siblingRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.value === "yes") {
      siblingSection.style.display = "block";

      document.getElementById('pet-modal').style.display = "block";
      const select = document.getElementById("pet-dropdown");
      if (select) {
          select.selectedIndex = 0; // first option (your placeholder)
      }
    } else {
      siblingSection.style.display = "none";
    }
  });
});

fosterRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.value === "Foster Home") {
      locationSection.style.display = "block";
            
      document.getElementById('foster-modal').style.display = "block";
      const select = document.getElementById("foster-dropdown");
      if (select) {
          select.selectedIndex = 0; // first option (your placeholder)
      }
    } else {
      locationSection.style.display = "none";
    }
  });
});

document.getElementById("add-pet-form").addEventListener("submit", async  (e) =>{
  e.preventDefault();

  const siblingSelected = document.querySelector('input[name="sibling"]:checked');
  const siblingValueInput = document.getElementById("pet-dropdown");

  // Only enforce requirement if "yes"
  if (siblingSelected && siblingSelected.value === "yes") {
      if (!siblingValueInput.value) {
          e.preventDefault(); // stop form submission
          alert("Please select a sibling pet.");
          openModal('pet-modal');
      }
  }

  const fosterSelected = document.querySelector('input[name="cur-location"]:checked');
  const fosterValueInput = document.getElementById("foster-dropdown");

  // Only enforce requirement if "Foster Home"
  if (fosterSelected && fosterSelected.value === "Foster Home") {
    if (!fosterValueInput.value) {
        e.preventDefault(); // stop form submission
        alert("Please select a foster family.");
        openModal('foster-modal');
    }
  }

  const form = document.getElementById("add-pet-form");
  const pet_photo = document.getElementById("pet-photo").files[0];
  const species = document.querySelector('input[name="species"]:checked')?.value;
  const fixed = document.querySelector('input[name="spayed-neutered"]:checked')?.value;
  const special_needs = document.querySelector('input[name="special-needs"]:checked')?.value;
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
  formData.append("pet_special_needs", special_needs)
  formData.append("pet_photo", pet_photo)
  formData.append("sibling_id", siblingValueInput.value)
  formData.append("foster_id", fosterValueInput.value)

  const response = await fetch("/addpet", {
      method: "POST",
      body: formData
  })

  const text = await response.text();
  console.log("RAW RESPONSE:", text);
})


