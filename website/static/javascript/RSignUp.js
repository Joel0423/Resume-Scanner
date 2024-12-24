// Add event listener to validate fields dynamically as the user types
document.getElementById("signupForm").addEventListener("input", (e) => {
    const fieldId = e.target.id;
    if (fieldId === "dob") {
      validateDOB();
    } else if (window[`validate${capitalize(fieldId)}`]) {
      window[`validate${capitalize(fieldId)}`]();
    }
  });
  
  // Toggle password visibility
  document.getElementById("togglePassword").addEventListener("click", () => {
    const passwordField = document.getElementById("password");
    const type = passwordField.type === "password" ? "text" : "password";
    passwordField.type = type;
    document.getElementById("togglePassword").classList.toggle("fa-eye-slash");
  });
  
  // Validation functions
  function validateName() {
    const nameField = document.getElementById("name");
    const nameValue = nameField.value.trim();
    const nameError = document.getElementById("nameError");
    const nameStatus = document.getElementById("nameStatus");
  
    // First, check the length requirement
    if (nameValue.length < 3) {
      showError(nameStatus, nameError, "Name must be at least 3 characters long");
      return;
    }
  
    // Then, validate allowed characters
    if (/^[A-Za-z ]+$/.test(nameValue)) {
      showSuccess(nameStatus, nameError);
    } else {
      showError(nameStatus, nameError, "Name must contain only letters and spaces");
    }
  }
  
  
  function validateEmail() {
    const emailField = document.getElementById("email");
    const emailValue = emailField.value.trim();
    const emailError = document.getElementById("emailError");
    const emailStatus = document.getElementById("emailStatus");
  
    if (/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(emailValue)) {
      showSuccess(emailStatus, emailError);
    } else {
      showError(emailStatus, emailError, "Enter a valid email address");
    }
  }
  
  function validatePassword() {
    const passwordField = document.getElementById("password");
    const passwordValue = passwordField.value.trim();
    const passwordError = document.getElementById("passwordError");
    const passwordStatus = document.getElementById("passwordStatus");
  
    if (/(?=.*[!@#$%^&*])(?=.*[0-9])(?=.{6,})/.test(passwordValue)) {
      showSuccess(passwordStatus, passwordError);
    } else {
      showError(
        passwordStatus,
        passwordError,
        "Password must be at least 6 characters with 1 special symbol and 1 number"
      );
    }
  }
  
  function validatePhone() {
    const phoneField = document.getElementById("phone");
    const phoneValue = phoneField.value.trim();
    const phoneError = document.getElementById("phoneError");
    const phoneStatus = document.getElementById("phoneStatus");
  
    if (/^\d{10}$/.test(phoneValue)) {
      showSuccess(phoneStatus, phoneError);
    } else {
      showError(phoneStatus, phoneError, "Phone number must be exactly 10 digits");
    }
  }
  
  function validateDOB() {
    const dobField = document.getElementById("dob");
    const dobValue = dobField.value;
    const dobError = document.getElementById("dobError");
    const dobStatus = document.getElementById("dobStatus");
  
    if (!dobValue) {
      showError(dobStatus, dobError, "Date of Birth is required");
      return;
    }
  
    const today = new Date();
    const dob = new Date(dobValue);
    const age = today.getFullYear() - dob.getFullYear();
    const isMonthPassed =
      today.getMonth() > dob.getMonth() ||
      (today.getMonth() === dob.getMonth() && today.getDate() >= dob.getDate());
  
    if (!isMonthPassed) {
      age--;
    }
  
    if (age >= 18) {
      showSuccess(dobStatus, dobError);
    } else {
      showError(dobStatus, dobError, "You must be at least 18 years old");
    }
  }
  
  function validateCompany() {
    const companyField = document.getElementById("company");
    const companyValue = companyField.value.trim();
    const companyError = document.getElementById("companyError");
    const companyStatus = document.getElementById("companyStatus");
  
    if (/^[A-Za-z ]+$/.test(companyValue)) {
      showSuccess(companyStatus, companyError);
    } else {
      showError(companyStatus, companyError, "Company name must contain only letters and spaces");
    }
  }
  
  function validateAddress() {
    const addressField = document.getElementById("address");
    const addressValue = addressField.value.trim();
    const addressError = document.getElementById("addressError");
  
    if (addressValue) {
      addressError.textContent = "";
    } else {
      addressError.textContent = "Company address cannot be empty";
    }
  }
  
  // Helper functions
  function showSuccess(statusElement, errorElement) {
    statusElement.className = "fas fa-check-circle success-icon";
    statusElement.style.display = "inline";
    errorElement.textContent = "";
    errorElement.classList.add("hidden");
  }
  
  function showError(statusElement, errorElement, errorMessage) {
    statusElement.className = "fas fa-times-circle error-icon";
    statusElement.style.display = "inline";
    errorElement.textContent = errorMessage;
    errorElement.classList.remove("hidden");
  }
  
  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  