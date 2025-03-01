document.addEventListener('DOMContentLoaded', function () {
    const submitBtn = document.getElementById('submit-btn');

    submitBtn.addEventListener('click', function () {
        const recruiterBtn = document.getElementById('recruiter-btn');
        const jobseekerBtn = document.getElementById('jobseeker-btn');

        if (recruiterBtn.classList.contains("active")) {
            window.location.href = "/r-sign-up";  // Redirect to Recruiter SignUp page
        } else if (jobseekerBtn.classList.contains("active")) {
            window.location.href = "/j-sign-up";  // Redirect to Jobseeker SignUp page
        } else {
            alert("Please select a role.");
        }
    });
});
