// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {

  function redirectToJobPage(job_id) {
    const jobId = job_id

    if (!jobId) {
      alert("Job ID is missing!");
      return;
    }

    window.location.href = `/view-job?job_id=${jobId}`;
  }

  async function saveJob(jobId) {
    try {
      const response = await fetch(`/save-job?job_id=${jobId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json(); // Parse JSON response

      // Display the response
      alert(data.message || data.error);
    } catch (error) {
      console.error("Error saving job:", error);
      alert("An error occurred. Please try again.");
    }
  }

  document.addEventListener("click", function (event) {
    if (event.target.classList.contains("job-button")) {
      const jobId = event.target.getAttribute("data-id");
      redirectToJobPage(jobId);
    }
    if (event.target.classList.contains("save-button")) {
      const jobId = event.target.getAttribute("data-id");
      saveJob(jobId);
    }
  });

  // Function to fetch profile summary data from backend API
  async function fetchProfileSummary() {
    try {
      const response = await fetch("/get-jobseek-stats"); // Replace with actual API endpoint
      if (!response.ok) throw new Error("Failed to fetch profile data");
      const data = await response.json();

      // Dynamically update profile summary on UI
      document.getElementById("resumesUploaded").textContent = data.total_resumes_count || 0;
      document.getElementById("jobsApplied").textContent = data.job_application_count || 0;
      document.getElementById("savedJobs").textContent = data.saved_job_count || 0;
    } catch (error) {
      console.error("Error fetching profile summary:", error);
    }
  }

  // Fetch profile data when the page loads
  fetchProfileSummary();


  fetch(`/get-all-jobs`)
    .then(response => response.json())
    .then(data => {
      displayJobs(data.jobs);
    })
    .catch(error => console.error("Error fetching jobs:", error));

  function displayJobs(jobs) {
    const jobList = document.getElementById("job-listings");
    jobList.innerHTML = "";
    num = 0;

    jobs.forEach(job => {
      const jobCard = `
                    <div class="col-md-4">
                        <div class="card mb-4 shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title">${job.title}</h5>
                                <h6 class="card-subtitle text-muted">${job.company}</h6>
                                <p class="card-text"><strong>Location:</strong> ${job.location}</p>
                                <p class="card-text"><strong>Salary:</strong> ${job.salary[0]}-${job.salary[1]}</p>
                                
                                <button class="btn btn-warning job-button w-100 my-2" data-id="${job.id}">Apply Now</button>
                                <button class="btn btn-outline-warning save-button w-100" data-id="${job.id}">Save for Later</button>
                            </div>
                        </div>
                    </div>
                `;
      jobList.innerHTML += jobCard;
      num++;
      if (num == 3)
        return;
    });
  }





});
