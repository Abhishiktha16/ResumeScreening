function uploadJob() {
    const jobFile = document.getElementById('jobDescription').files[0];
    const formData = new FormData();
    formData.append("job_description", jobFile);
  
    fetch("/post_job", {
        method: "POST",
        body: formData,
    })
        .then((res) => res.json())
        .then((data) => {
            document.getElementById("jobStatus").textContent = data.message;
        });
  }
  
  function applyJob() {
    const name = document.getElementById('jobSeekerName').value;
    const email = document.getElementById('jobSeekerEmail').value;
    const resume = document.getElementById('resume').files[0];
    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("resume", resume);
  
    fetch("/upload_resume", {
        method: "POST",
        body: formData,
    })
        .then((res) => res.json())
        .then((data) => {
            document.getElementById("applicationStatus").textContent = data.message;
        });
  }
  