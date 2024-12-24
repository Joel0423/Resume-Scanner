// Toggle password visibility
function togglePassword() {
  const passwordField = document.getElementById("password");
  const eyeIcon = document.getElementById("eyeIcon");

  // Toggle password type and eye icon
  if (passwordField.type === "password") {
    passwordField.type = "text";
    eyeIcon.classList.remove("fa-eye");
    eyeIcon.classList.add("fa-eye-slash");
  } else {
    passwordField.type = "password";
    eyeIcon.classList.remove("fa-eye-slash");
    eyeIcon.classList.add("fa-eye");
  }
}

function validateForm() {
  const username = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username) {
    alert("Please enter your email");
    return;
  }
  if (!password) {
    alert("Please enter your password");
    return;
  }

  alert("Login Successful!");
}
