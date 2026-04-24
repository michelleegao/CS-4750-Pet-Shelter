const deleteButton = document.getElementById("delete-btn");

document.getElementById("edit-user-form").addEventListener("submit", async  (e) =>{
    console.log("SUBMIT FIRED");
    e.preventDefault();
  
    const form = document.getElementById("edit-user-form");
    const userId = document.getElementById("edit-userid").value;
    const managees = Array.from(
        document.querySelectorAll('input[name="managed-employees"]:checked')
    ).map(el => el.value);

    const formData = new FormData();
    formData.append("user_role", document.getElementById("role-dropdown").value)
    formData.append("manager_status", document.querySelector('input[name="manager-status"]:checked')?.value)
    formData.append("managed_employees", JSON.stringify(managees))

    formData.append("action", "update")

  
    const response = await fetch(`/users/${userId}`, {
        method: "POST",
        body: formData
    })
  
    const text = await response.text();
    console.log("RAW RESPONSE:", text);

    window.location.href = `/users/${userId}`;
});

deleteButton.addEventListener("click", async function(){
    const userId = this.dataset.id;

    const response = await fetch(`/delete_user/${userId}`, {
      method: "POST"
    });

    if (response.ok) {
      // remove pet from UI
      window.location.href = "/users_search";
    }
})