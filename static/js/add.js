
function openModal(id){
    document.getElementById(id).style.display = "block";
  }
  
  function closeModal(id) {
    document.getElementById(id).style.display = "none";
  }
  
  function saveModalValue(id) {
    const value = document.getElementById("modal-input").value;
  
    // store value into hidden input in main form
    document.getElementById(id).value = value;
  
    closeModal();
    }
