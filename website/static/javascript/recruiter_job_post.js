let currentPage = 1;

function fetchJobs(page = 1, containerId = "job-listings") {
    const title = document.getElementById("search-title")?.value || "";
    const location = document.getElementById("search-location")?.value || "";
    const company = document.getElementById("search-company")?.value || "";
    const minSalary = document.getElementById("min-salary")?.value || 0;
    const maxSalary = document.getElementById("max-salary")?.value || 999999;

    fetch(`/get-r-jobs?title=${title}&location=${location}&company=${company}&salary_min=${minSalary}&salary_max=${maxSalary}&page=${page}`)
        .then(response => response.json())
        .then(data => {
            currentPage = page;

            if (containerId === "homepage-job-list") {
                displayJobs(data.jobs.slice(0, 3), containerId); // Show only 3 jobs on homepage
            } else {
                displayJobs(data.jobs, containerId);
                setupPagination(data.total_pages);
            }
        })
        .catch(error => console.error("Error fetching jobs:", error));
}

function displayJobs(jobs, containerId) {
    const jobList = document.getElementById(containerId);
    if (!jobList) return; // Prevent errors if the container is missing
    jobList.innerHTML = "";

    jobs.forEach(job => {
        const jobCard = `
            <div class="col-md-4">
                <div class="job-card mb-4 shadow-sm fade-in p-3">
                    <div class="card-body">
                        <h5 class="card-title">${job.title}</h5>
                        <h6 class="card-subtitle text-muted">${job.company}</h6>
                        <p class="card-text"><strong>Location:</strong> ${job.location}</p>
                        <p class="card-text"><strong>Salary:</strong> ${job.salary[0]} - ${job.salary[1]}</p>
                        <button class="btn btn-warning job-button w-100 my-2" onclick="redirectToCandidatePage(${job.id})">View candidates</button>
                    </div>
                </div>
            </div>
        `;
        jobList.innerHTML += jobCard;
    });

     // Add the "Explore More" button after the job listings
    if (jobs.length > 0) {
        const exploreMoreButton = document.createElement("div");
        exploreMoreButton.classList.add("text-center", "mt-4");
        exploreMoreButton.innerHTML = `
            <button id="exploreMoreBtn" class="btn btn-primary px-4 py-2">Explore More</button>
        `;
        jobList.parentElement.appendChild(exploreMoreButton);

        // Add event listener for navigation
        document.getElementById("exploreMoreBtn").addEventListener("click", function () {
            window.location.href = "/recruiter_job_posts"; // Change this to the correct route
        });
    }

}
