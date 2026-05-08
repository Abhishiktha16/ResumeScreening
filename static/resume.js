// Upload Job Function
function uploadJob() {
  const jobFile = document.getElementById('jobDescription').files[0];
  const formData = new FormData();
  formData.append("job_description", jobFile);

  fetch("/post_job", { // Updated to match the Flask route
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("jobStatus").textContent = data.message;
    })
    .catch((error) => {
      console.error("Error uploading job:", error);
      document.getElementById("jobStatus").textContent =
        "An error occurred while uploading the job.";
    });
}

// Apply Job Function
function applyJob() {
  const name = document.getElementById('jobSeekerName').value;
  const email = document.getElementById('jobSeekerEmail').value;
  const resume = document.getElementById('resume').files[0];

  const formData = new FormData();
  formData.append("name", name);
  formData.append("email", email);
  formData.append("resume", resume);

  fetch("/upload_resume", { // Updated to match the Flask route
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("applicationStatus").textContent = data.message;
    })
    .catch((error) => {
      console.error("Error applying for job:", error);
      document.getElementById("applicationStatus").textContent =
        "An error occurred while applying for the job.";
    });
}

// Process Resumes Function
function processResumes() {
  fetch("/process_resumes") // Updated to match the Flask route
    .then((res) => res.json())
    .then((data) => {
      let tableHTML = `<table border="1">
        <thead><tr><th>Name</th><th>Email</th><th>Score</th></tr></thead><tbody>`;
      data.forEach((applicant) => {
        tableHTML += `<tr>
          <td>${applicant.name}</td>
          <td>${applicant.email}</td>
          <td>${applicant.score}</td>
        </tr>`;
      });
      tableHTML += `</tbody></table>`;
      document.getElementById("results").innerHTML = tableHTML;
    })
    .catch((error) => {
      console.error("Error processing resumes:", error);
      document.getElementById("results").innerHTML =
        "An error occurred while processing resumes.";
    });
}
