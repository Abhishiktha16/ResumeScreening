import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_USER = 'mopuriabhi16@gmail.com'
MAIL_PASS = 'xnow kvjt pyoi pejk'  # your app password

msg = MIMEMultipart()
msg['From']    = MAIL_USER
msg['To']      = MAIL_USER  # sending to yourself
msg['Subject'] = 'ResumeScreen Test'
msg.attach(MIMEText('If you see this, email works!', 'plain'))

try:
    print("Step 1: Connecting to Gmail...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
    print("Step 2: Connected. Starting TLS...")
    server.ehlo()
    server.starttls()
    server.ehlo()
    print("Step 3: TLS started. Logging in...")
    server.login(MAIL_USER, MAIL_PASS)
    print("Step 4: Logged in. Sending...")
    server.sendmail(MAIL_USER, MAIL_USER, msg.as_string())
    server.quit()
    print("SUCCESS - check your inbox!")
except smtplib.SMTPAuthenticationError:
    print("FAILED - Authentication error. App Password is wrong.")
    print("Follow these steps exactly:")
    print("1. Go to myaccount.google.com")
    print("2. Security → turn ON 2-Step Verification")
    print("3. Search 'App Passwords' in the search bar")
    print("4. Generate new password for Mail")
    print("5. Copy the 16-char password with spaces")
except Exception as e:
    print(f"FAILED - {type(e).__name__}: {e}")