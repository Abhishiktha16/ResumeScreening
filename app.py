from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os, sqlite3, uuid, threading
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import pdfplumber

app = Flask(__name__)
app.secret_key = 'resume_screen_secret'
app.config['UPLOAD_FOLDER'] = 'uploads'

# MAIL CONFIGURATION
app.config['MAIL_SERVER']        = 'smtp.gmail.com'
app.config['MAIL_PORT']          = 587
app.config['MAIL_USE_TLS']       = True
app.config['MAIL_USERNAME']      = 'mopuriabhi16@gmail.com'
app.config['MAIL_PASSWORD']      = 'xnow kvjt pyoi pejk'  # ← spaces added
app.config['MAIL_DEFAULT_SENDER'] = 'mopuriabhi16@gmail.com'

bcrypt = Bcrypt(app)
mail   = Mail(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'resume.db')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    return sqlite3.connect(DB_PATH)

def parse_datetime(val):
    if val and isinstance(val, str):
        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
            try: return datetime.strptime(val, fmt)
            except ValueError: pass
    return val

def parse_jobs(raw_jobs):
    return [tuple([*j[:6], parse_datetime(j[6]), *j[7:]]) for j in raw_jobs]

def extract_text_from_pdf(filepath):
    try:
        with pdfplumber.open(filepath) as pdf:
            return "".join(p.extract_text() or "" for p in pdf.pages).lower()
    except Exception:
        return ""

def calculate_matching_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0
    r, j  = set(resume_text.split()), set(jd_text.split())
    total = r | j
    return round(min(len(r & j) / len(total) * 100, 100), 2) if total else 0

def unique_filename(original):
    ext = os.path.splitext(secure_filename(original))[1]
    return f"{uuid.uuid4().hex}{ext}"


# ── EMAIL (runs in background thread so it never blocks the app) ──

def send_result_email(to_email, name, job_profile, company, score, status):
    """Send email in a background thread — app never waits for this."""
    def _send():
        try:
            if status == "Selected":
                subject = f"Congratulations! You're selected for {job_profile} at {company}"
                body = f"""Dear {name},

We are pleased to inform you that your application for {job_profile} at {company} has been reviewed.

Your resume matched {score}% with our requirements and you have been SELECTED for the next round.

Our HR team will reach out to you shortly.

Best regards,
{company} HR Team
ResumeScreen Platform"""
            else:
                subject = f"Application Update — {job_profile} at {company}"
                body = f"""Dear {name},

Thank you for applying for {job_profile} at {company}.

After reviewing your resume, we regret that your profile does not match our current requirements (match score: {score}%).

We encourage you to apply for future openings.

Best regards,
{company} HR Team
ResumeScreen Platform"""

            with app.app_context():
                msg = Message(
                    subject,
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[to_email]
                )
                msg.body = body
                mail.send(msg)
                print(f"✅ Email sent to {to_email}")

        except Exception as e:
            # Log but never crash — email failure should not affect the user
            print(f"❌ Email failed: {e}")

    # Fire and forget — runs in background
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


# ── SHARED ───────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('hr_email', None)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ── HR ───────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute("SELECT email FROM hr_users WHERE email=?", (email,))
            if cur.fetchone():
                return render_template('register.html', error="Email already registered.")
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("INSERT INTO hr_users (email, password) VALUES (?,?)", (email, hashed))
            conn.commit()
            return redirect(url_for('hr_login'))
        except sqlite3.Error as e:
            conn.rollback()
            return render_template('register.html', error="Registration failed: " + str(e))
        finally:
            cur.close(); conn.close()
    return render_template('register.html')


@app.route('/hr_login', methods=['GET', 'POST'])
def hr_login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute("SELECT email, password FROM hr_users WHERE email=?", (email,))
            user = cur.fetchone()
            if user and bcrypt.check_password_hash(user[1], password):
                session['hr_email'] = user[0]
                return redirect(url_for('hr_dash'))
            return render_template('hr_login.html',
                                   error="Invalid password." if user else "Email not found.")
        except sqlite3.Error as e:
            return render_template('hr_login.html', error="Database error: " + str(e))
        finally:
            cur.close(); conn.close()
    return render_template('hr_login.html')


@app.route('/hr_dash')
def hr_dash():
    if 'hr_email' not in session:
        return redirect(url_for('hr_login'))
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, company, job_profile, salary, job_description, posted_by, posted_at
            FROM jobs WHERE posted_by=? ORDER BY id DESC
        """, (session['hr_email'],))
        raw = cur.fetchall()
        jobs = []
        for job in raw:
            cur.execute("SELECT COUNT(*) FROM resumes WHERE job_id=?", (job[0],))
            jobs.append(tuple(job) + (cur.fetchone()[0],))
        return render_template('hr_dash.html', jobs=parse_jobs(jobs), hr_email=session['hr_email'])
    except sqlite3.Error as e:
        return render_template('hr_dash.html', jobs=[], hr_email=session['hr_email'],
                               error="Database error: " + str(e))
    finally:
        cur.close(); conn.close()


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'hr_email' not in session:
        return redirect(url_for('hr_login'))
    if request.method == 'POST':
        company = request.form['company']
        profile = request.form['job_profile']
        salary  = request.form['salary']
        file    = request.files.get('job_description')
        if not file or not file.filename:
            return render_template('post_job.html', error="Please select a PDF file.")
        if not file.filename.lower().endswith('.pdf'):
            return render_template('post_job.html', error="Only PDF files are accepted.")
        filename = unique_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO jobs (company,job_profile,salary,job_description,posted_by,posted_at) VALUES (?,?,?,?,?,?)",
                (company, profile, salary, filename, session['hr_email'], datetime.now()))
            conn.commit()
            return redirect(url_for('hr_dash'))
        except sqlite3.Error as e:
            conn.rollback()
            return render_template('post_job.html', error="Failed to post job: " + str(e))
        finally:
            cur.close(); conn.close()
    return render_template('post_job.html')


@app.route('/applicants/<int:job_id>')
def job_applicants(job_id):
    if 'hr_email' not in session:
        return redirect(url_for('hr_login'))
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("SELECT id,company,job_profile,salary FROM jobs WHERE id=? AND posted_by=?",
                    (job_id, session['hr_email']))
        job = cur.fetchone()
        if not job:
            return redirect(url_for('hr_dash'))
        ranked = request.args.get('ranked', '0') == '1'
        cur.execute(f"""
            SELECT name,email,filename,score,status,uploaded_at
            FROM resumes WHERE job_id=? ORDER BY {'score DESC' if ranked else 'uploaded_at ASC'}
        """, (job_id,))
        applicants = [(i,) + tuple([*r[:5], parse_datetime(r[5])])
                      for i, r in enumerate(cur.fetchall(), 1)]
        return render_template('job_applicants.html',
                               job=job, applicants=applicants, ranked=ranked)
    except sqlite3.Error:
        return redirect(url_for('hr_dash'))
    finally:
        cur.close(); conn.close()


@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'hr_email' not in session:
        return redirect(url_for('hr_login'))
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM jobs WHERE id=? AND posted_by=?", (job_id, session['hr_email']))
        if cur.fetchone():
            cur.execute("DELETE FROM resumes WHERE job_id=?", (job_id,))
            cur.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            conn.commit()
    except sqlite3.Error:
        conn.rollback()
    finally:
        cur.close(); conn.close()
    return redirect(url_for('hr_dash'))


# ── JOB SEEKER ───────────────────────────────────────────────

@app.route('/job_seeker', methods=['GET', 'POST'])
def job_seeker():
    if 'hr_email' in session:
        return redirect(url_for('hr_dash'))
    conn = get_db(); cur = conn.cursor()

    def fetch_jobs():
        cur.execute("SELECT id,company,job_profile,salary,job_description,posted_by,posted_at FROM jobs ORDER BY id DESC")
        return parse_jobs(cur.fetchall())

    if request.method == 'POST':
        job_id = request.form.get('job_id')
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip()
        file   = request.files.get('resume')

        if not name or not email:
            jobs = fetch_jobs(); cur.close(); conn.close()
            return render_template('job_seeker.html', jobs=jobs, error="Name and email are required.")
        if not file or not file.filename:
            jobs = fetch_jobs(); cur.close(); conn.close()
            return render_template('job_seeker.html', jobs=jobs, error="Please select a PDF resume.")
        if not file.filename.lower().endswith('.pdf'):
            jobs = fetch_jobs(); cur.close(); conn.close()
            return render_template('job_seeker.html', jobs=jobs, error="Only PDF resumes are accepted.")

        filename    = unique_filename(file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(resume_path)

        try:
            cur.execute("SELECT company,job_profile,job_description FROM jobs WHERE id=?", (job_id,))
            job = cur.fetchone()
            if not job:
                cur.close(); conn.close()
                return render_template('job_seeker.html', error="Job not found.")

            company, job_profile, jd_filename = job
            score  = calculate_matching_score(
                extract_text_from_pdf(resume_path),
                extract_text_from_pdf(os.path.join(app.config['UPLOAD_FOLDER'], jd_filename))
            )
            status = "Selected" if score >= 70 else "Rejected"

            cur.execute(
                "INSERT INTO resumes (name,email,filename,job_id,score,status,uploaded_at) VALUES (?,?,?,?,?,?,?)",
                (name, email, filename, int(job_id), score, status, datetime.now()))
            conn.commit()

            # ✅ Email fires in background — user gets result instantly
            send_result_email(email, name, job_profile, company, score, status)

            cur.close(); conn.close()
            return render_template('job_seeker.html', jobs=None,
                                   applied_job={'id': job_id, 'company': company,
                                                'job_profile': job_profile},
                                   name=name, score=score, status=status)

        except sqlite3.Error as e:
            conn.rollback(); cur.close(); conn.close()
            return render_template('job_seeker.html', error="Database error: " + str(e))

    jobs = fetch_jobs(); cur.close(); conn.close()
    return render_template('job_seeker.html', jobs=jobs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)