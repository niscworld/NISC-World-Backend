import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, message_body):
    from_email = 'nisc.co.in@gmail.com'
    app_password = 'gtdl lscl nnhi jiwa'

    # Create the email message
    msg = MIMEText(message_body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        return False

