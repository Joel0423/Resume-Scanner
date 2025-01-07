// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const mobileMenu = document.getElementById("mobile-menu");

  // Ensure both elements exist
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener("click", () => {
      // Toggle visibility
      mobileMenu.classList.toggle("hidden");
      mobileMenu.classList.toggle("block");
    });
  } else {
    console.error("Menu toggle or mobile menu element not found!");
  }

  // Function to fetch profile summary data from backend API
  async function fetchProfileSummary() {
    try {
      const response = await fetch("/api/profile-summary"); // Replace with actual API endpoint
      if (!response.ok) throw new Error("Failed to fetch profile data");
      const data = await response.json();

      // Dynamically update profile summary on UI
      document.getElementById("resumesUploaded").textContent = data.resumes_uploaded || 0;
      document.getElementById("jobsApplied").textContent = data.jobs_applied || 0;
      document.getElementById("savedJobs").textContent = data.saved_jobs || 0;
    } catch (error) {
      console.error("Error fetching profile summary:", error);
    }
  }

  document.getElementById("logout-link").addEventListener("click", function (e) {
    e.preventDefault(); // Prevent default action of anchor tag
  
    // Clear tokens/session storage or cookies
    localStorage.removeItem("authToken"); // Example for JWT
    sessionStorage.clear();
  
    // Redirect user to login page or home
    window.location.href = "/templates/landing.html";
  });

  // Fetch profile data when the page loads
  fetchProfileSummary();

  // Function to handle resume upload button
  document.getElementById("upload-resume")?.addEventListener("click", () => {
    alert("Resume uploaded successfully!");
    // Add actual backend logic if required
  });
});
