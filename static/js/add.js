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
            const select = document.getElementById(dropdown_id);
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
        if (radio.value === "Foster") {
            locationSection.style.display = "block";
            
            document.getElementById('foster-modal').style.display = "block";
            const select = document.getElementById(dropdown_id);
            if (select) {
                select.selectedIndex = 0; // first option (your placeholder)
            }
        } else {
            locationSection.style.display = "none";
        }
    });
  });

