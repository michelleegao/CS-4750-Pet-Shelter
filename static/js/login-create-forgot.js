// LOGIN
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.success) {
      showMessage("Login successful! Redirecting...", "green");
      setTimeout(() => {
        window.location.href = "/pets_search";
      }, 1000);
    } else {
      showMessage("Incorrect email or password.", "red");
    }
  });
}

// CREATE ACCOUNT
const createForm = document.getElementById("createForm");

if (createForm) {
  createForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const firstName = document.getElementById("firstName").value;
    const lastName = document.getElementById("lastName").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const phoneNumber = document.getElementById("phoneNumber").value;
    const positionName = document.getElementById("positionName").value;

    if (password !== confirmPassword) {
      showMessage("Passwords do not match.", "red");
      return;
    }

    const res = await fetch("/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        firstName,
        lastName,
        email,
        phoneNumber,
        positionName,
        password
      })
    });

    const data = await res.json();

    if (data.success) {
      showMessage("Account successfully created!", "green");
      setTimeout(() => {
        window.location.href = "/";
      }, 1200);
    } else {
      showMessage(data.message || "Signup failed.", "red");
    }
  });
}

// FORGOT PASSWORD
let verifiedUser = null;

const checkUserBtn = document.getElementById("checkUserBtn");
const resetBtn = document.getElementById("resetBtn");

if (checkUserBtn) {
  checkUserBtn.addEventListener("click", async function () {
    const email = document.getElementById("forgotUsername").value;

    const res = await fetch("/check_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    const data = await res.json();
    const messageBox = document.getElementById("messageBox");

    if (data.exists) {
      verifiedUser = email;
      messageBox.innerText = "User found. Enter new password.";
      messageBox.style.color = "green";
      document.getElementById("resetSection").style.display = "block";
      checkUserBtn.style.display = "none";
    } else {
      messageBox.innerText = "User not found.";
      messageBox.style.color = "red";
    }
  });
}

if (resetBtn) {
  resetBtn.addEventListener("click", async function () {
    const newPassword = document.getElementById("newPassword").value;

    const res = await fetch("/reset_password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: verifiedUser,
        newPassword
      })
    });

    const data = await res.json();
    const messageBox = document.getElementById("messageBox");

    if (data.success) {
      messageBox.innerText = "Password reset successful!";
      messageBox.style.color = "green";
    } else {
      messageBox.innerText = "Reset failed.";
      messageBox.style.color = "red";
    }
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