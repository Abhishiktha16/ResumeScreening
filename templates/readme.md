# Resume Screening App — Setup & Run Guide

## Folder Structure
```
resume_project/
├── app.py
├── init_db.py
├── uploads/              ← auto-created on first run
└── templates/
    ├── index.html        ← your existing file (unchanged)
    ├── hr_login.html     ← your existing file (unchanged)
    ├── register.html     ← your existing file (unchanged)
    ├── post_job.html     ← your existing file (unchanged)
    ├── hr_dash.html      ← UPDATED
    ├── job_seeker.html   ← UPDATED
    ├── job_applicants.html ← NEW
    └── 404.html          ← your existing file (unchanged)
```

---

## Step-by-Step Setup

### 1. Install dependencies
```bash
pip install flask flask-bcrypt pdfplumber werkzeug
```

### 2. Initialise the database (run once)
```bash
python init_db.py
```
This creates `resume.db` with three tables: `hr_users`, `jobs`, `resumes`.

### 3. Start the app
```bash
python app.py
```
Open your browser at: **http://127.0.0.1:5001**

---

## What's New

### HR Dashboard (`/hr_dash`)
- Each job card shows **applicant count**.
- **View Applicants** button → shows all applicants in submission order.
- **Rank by Score** button → same page, re-sorted by matching score (highest first), with gold/silver/bronze medals for top 3.
- **Delete Job** button → removes the job AND all its applicant records from the database, and it disappears from the job seeker page instantly.

### Applicants Page (`/applicants/<job_id>`)  — HR only
- Full table: Rank, Name, Email, Score (with visual bar), Status badge, Resume PDF link, Applied date.
- Toggle between submission order and ranked order with one click.

### Separation of HR and Job Seeker
- If an **HR user** (logged in) visits `/job_seeker`, they are redirected to the HR dashboard.
- **Job seekers** only ever see their own matching score and status — never any rankings or other applicants' data.
- The `/applicants/<job_id>` route checks `session['hr_email']` and redirects to login if not present.

---

## User Flows

### HR
1. `/register` → create account
2. `/hr_login` → login
3. `/hr_dash` → see all posted jobs
4. `/post_job` → upload a new job with PDF description
5. Click **View Applicants** or **Rank by Score** on any job card
6. Click **Delete Job** to remove a job from the portal

### Job Seeker
1. Go to `/job_seeker` (no login needed)
2. Browse available jobs, click **Apply Now**
3. Fill name, email, upload resume PDF
4. See only **your own** matching score and Selected/Rejected status
