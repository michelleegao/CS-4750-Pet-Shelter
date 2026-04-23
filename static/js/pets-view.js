const editModal = document.getElementById("editModal");
const closeEditModal = document.getElementById("closeEditModal");
const cancelEditModal = document.getElementById("cancelEditModal");
const closeDeleteModal = document.getElementById("closeDeleteModal");
const cancelDeleteModal = document.getElementById("cancelDeleteModal");
const deleteModal = document.getElementById("deleteModal");


function openEditModal(button){
    console.log(button.dataset);
    editModal.classList.add("show");

    const fixedValue = button.dataset.fixed;
    const locationValue = button.dataset.curLocation;
    const specialNeeds = button.dataset.specialNeeds;
    document.querySelector(
        `input[name="fixed"][value="${fixedValue}"]`
    ).checked = true;

    document.querySelector(
        `input[name="location"][value="${locationValue}"]`
    ).checked = true;

    document.querySelector(
        `input[name="special-needs"][value="${specialNeeds}"]`
    ).checked = true;
            
    document.getElementById("edit-name").value = button.dataset.name;
    document.getElementById("edit-breed").value = button.dataset.breed;
    document.getElementById("edit-age").value = button.dataset.age;
    document.getElementById("edit-weight").value = button.dataset.weight;
    document.getElementById("edit-notes").value = button.dataset.description;
    document.getElementById("edit-photo").src = button.dataset.photo;
    document.getElementById("adoption-dropdown").value = button.dataset.adoption;
    document.getElementById("foster-dropdown").value = button.dataset.fosterId;
    document.getElementById("edit-petid").value = button.dataset.id;
    document.getElementById("adoptive-families-dropdown").value = button.dataset.adoptiveFamily;
}

closeEditModal.addEventListener("click", () => {
    editModal.classList.remove("show");
});

cancelEditModal.addEventListener("click", () => {
    editModal.classList.remove("show");
});

editModal.addEventListener("click", (e) => {
    if (e.target === editModal) {
        editModal.classList.remove("show");
    }
});

function openDeleteModal(button){
    console.log(button.dataset);
    deleteModal.classList.add("show");

    document.getElementById("delete-petid").value = button.dataset.id;
    document.getElementById("delete-photo").src = button.dataset.photo;
    document.getElementById("delete-adoption-dropdown").value = button.dataset.adoption;
}

closeDeleteModal.addEventListener("click", () => {
    deleteModal.classList.remove("show");
});

cancelDeleteModal.addEventListener("click", () => {
    deleteModal.classList.remove("show");
});

deleteModal.addEventListener("click", (e) => {
    if (e.target === deleteModal) {
        deleteModal.classList.remove("show");
    }
});

// Delete Pet Submission Section 
document.getElementById("previous-pet-form").addEventListener("submit", async  (e) =>{
    e.preventDefault();
  
    const form = document.getElementById("previous-pet-form");
    const petId = document.getElementById("delete-petid").value;

    const formData = new FormData();
    formData.append("pet_deletion_reason", document.getElementById("delete-reason").value)
    formData.append("pet_id", document.getElementById("delete-petid").value)
    formData.append("pet_adoption", document.getElementById("delete-adoption-dropdown").value)
    formData.append("pet_adoption_family", document.getElementById("delete-adoptive-families-dropdown").value)
    formData.append("action", "delete")

  
    const response = await fetch(`/pet/${petId}`, {
        method: "POST",
        body: formData
    })
  
    const text = await response.text();
    console.log("RAW RESPONSE:", text);

    window.location.href = `/pet/${petId}`;
  })


// Edit Pet Submission Section
document.getElementById("edit-pet-form").addEventListener("submit", async  (e) =>{
    e.preventDefault();

    const fosterSelected = document.querySelector('input[name="location"]:checked');
    const fosterValueInput = document.getElementById("foster-dropdown");

    // Only enforce requirement if "Foster Home"
    if (fosterSelected && fosterSelected.value === "Foster Home") {
        if (!fosterValueInput.value) {
            e.preventDefault(); // stop form submission
            alert("Please select a foster family.");
        }
    }
  
    const form = document.getElementById("edit-pet-form");
    const pet_photo = document.getElementById("pet-photo").files[0]; // could be null
    const fixed = document.querySelector('input[name="fixed"]:checked')?.value;
    const cur_location = document.querySelector('input[name="location"]:checked')?.value;
    const special_needs = document.querySelector('input[name="special-needs"]:checked')?.value;
    const petId = document.getElementById("edit-petid").value;

    const formData = new FormData();
    formData.append("pet_name", document.getElementById("edit-name").value)
    formData.append("pet_age", document.getElementById("edit-age").value)
    formData.append("pet_description", document.getElementById("edit-notes").value)
    formData.append("pet_fixed", fixed)
    formData.append("pet_curr_location", cur_location)
    formData.append("foster_id", fosterValueInput.value)
    formData.append("pet_breed", document.getElementById("edit-breed").value)
    formData.append("pet_weight", document.getElementById("edit-weight").value)
    formData.append("pet_special_needs", special_needs)
    formData.append("pet_photo", pet_photo)
    formData.append("pet_id", document.getElementById("edit-petid").value)
    formData.append("pet_adoption", document.getElementById("adoption-dropdown").value)
    formData.append("pet_adoption_family", document.getElementById("adoptive-families-dropdown").value)
    formData.append("action", "update")

  
    const response = await fetch(`/pet/${petId}`, {
        method: "POST",
        body: formData
    })
  
    const text = await response.text();
    console.log("RAW RESPONSE:", text);

    window.location.href = `/pet/${petId}`;
  })