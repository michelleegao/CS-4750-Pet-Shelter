// LOGIN
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const users = JSON.parse(localStorage.getItem("users")) || [];

    const user = users.find(
      u => u.username === username && u.password === password
    );

    if (user) {
      showMessage("Login successful! Redirecting...", "green");

      setTimeout(() => {
        window.location.href = "petsearch.html";
      }, 1000);

    } else {
      showMessage("Incorrect username or password.", "red");
    }
  });
}

// CREATE ACCOUNT
const createForm = document.getElementById("createForm");

if (createForm) {
  createForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const firstName = document.getElementById("firstName").value;
    const lastName = document.getElementById("lastName").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
      showMessage("Passwords do not match.", "red");
      return;
    }

    let users = JSON.parse(localStorage.getItem("users")) || [];

    const exists = users.find(u => u.username === username);

    if (exists) {
      showMessage("Username already exists.", "red");
      return;
    }

    users.push({ firstName, lastName, username, password });

    localStorage.setItem("users", JSON.stringify(users));

    showMessage("Account successfully created!", "green");

    setTimeout(() => {
      window.location.href = "login.html";
    }, 1200);
  });
}

// FORGOT PASSWORD
const forgotForm = document.getElementById("forgotForm");

if (forgotForm) {
  forgotForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const username = document.getElementById("forgotUsername").value;
    const users = JSON.parse(localStorage.getItem("users")) || [];

    const user = users.find(u => u.username === username);

    if (user) {
      showMessage("User found! Enter a new password.", "green");
      document.getElementById("resetSection").style.display = "block";
    } else {
      showMessage("Username not found.", "red");
    }
  });
}

// RESET PASSWORD BUTTON
const resetBtn = document.getElementById("resetBtn");

if (resetBtn) {
  resetBtn.addEventListener("click", function () {
    const username = document.getElementById("forgotUsername").value;
    const newPassword = document.getElementById("newPassword").value;

    let users = JSON.parse(localStorage.getItem("users")) || [];

    users = users.map(u => {
      if (u.username === username) {
        u.password = newPassword;
      }
      return u;
    });

    localStorage.setItem("users", JSON.stringify(users));

    showMessage("Password successfully reset!", "green");
  });
}

// MESSAGE FUNCTION
function showMessage(text, color) {
  let msg = document.getElementById("formMessage");

  if (!msg) {
    msg = document.createElement("p");
    msg.id = "formMessage";
    msg.style.marginTop = "15px";

    const container = document.querySelector(".login-container") || document.body;
    container.appendChild(msg);
  }

  msg.textContent = text;
  msg.style.color = color;
}