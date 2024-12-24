document.addEventListener('DOMContentLoaded', function () {
    const submitBtn = document.getElementById('submit-btn');

    submitBtn.addEventListener('click', function () {
        const recruiterRadio = document.getElementById('recruiter');
        const jobseekerRadio = document.getElementById('jobseeker');

        if (recruiterRadio.checked) {
            window.location.href = "/r-sign-up";  // Redirect to Recruiter SignUp page
        } else if (jobseekerRadio.checked) {
            window.location.href = "/j-sign-up";  // Redirect to Jobseeker SignUp page
        } else {
            alert("Please select a role.");
        }
    });
});
