// recruiter_homepage.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("Recruiter Homepage Loaded");
  
    // Carousel auto-slide configuration
    let carousel = document.querySelector('#heroCarousel');
    let carouselInstance = new bootstrap.Carousel(carousel, {
      interval: 3000, // 3 seconds
      ride: 'carousel'
    });
  
    // Example for adding event listeners if needed in the future
    document.querySelectorAll('.card').forEach(card => {
      card.addEventListener('click', () => {
        alert('Card clicked!');
      });
    });

    document.getElementById("logout-link").addEventListener("click", function (e) {
        e.preventDefault(); // Prevent default action of anchor tag
      
        // Clear tokens/session storage or cookies
        localStorage.removeItem("authToken"); // Example for JWT
        sessionStorage.clear();
      
        // Redirect user to login page or home
        window.location.href = "/landing";
      });
      
  });
  