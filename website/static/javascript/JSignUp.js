document.getElementById("signupForm").addEventListener("input", (e) => {
    const fieldId = e.target.id;
    if (fieldId === "dob") {
      validateDOB();
    } else if (window[`validate${capitalize(fieldId)}`]) {
      window[`validate${capitalize(fieldId)}`]();
    }
  });
  
 
  
  // Validation functions
 
  function validateProfilePic() {
    const picField = document.getElementById("profilePic");
    const errorField = document.getElementById("profilePicError");
  
    if (picField.files[0] && picField.files[0].size > 10 * 1024 * 1024) {
      errorField.textContent = "File size must not exceed 10 MB";
      errorField.classList.remove("hidden");
    } else {
      errorField.textContent = "";
      errorField.classList.add("hidden");
    }
  }
  
  // Helper functions remain the same...
  