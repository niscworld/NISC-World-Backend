import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import threading

from config import GeneralSettings

def send_email(name, to_email, subject, message_body):
    from_email = GeneralSettings.FROM_EMAIL
    app_password = GeneralSettings.MAIL_PASS_KEY

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = from_email
    msg.add_header('Reply-To', from_email)

    message = f"""
{message_body}

From,
{name}
{to_email}
"""

    # Plain text version (important)
    text_part = MIMEText(message, 'plain')
    msg.attach(text_part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(from_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_email_to(name, to_email, subject, message):
    from_email = GeneralSettings.FROM_EMAIL
    app_password = GeneralSettings.MAIL_PASS_KEY

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.add_header('Reply-To', from_email)

    # Attach plain-text message
    text_part = MIMEText(message, 'plain')
    msg.attach(text_part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(from_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[MAIL ERROR] Failed to send email: {e}")
        return False

def send_otp_email(name, to_email, otp, purpose="Verification"):
    subject = f"NISC World: OTP for {purpose}"
    message_body = f"""
Hello {name},

Your One-Time Password (OTP) for {purpose} is:

🔐 OTP: {otp}

This code will expire in 15 Minutes. Please do not share it with anyone.

Thank you,
NISC Security Team
"""

    return send_email_to(name=name, to_email=to_email, subject=subject, message=message_body)



def send_email_with_attachment(to_email, subject, body, attachment_path, filename):
    """
    Send email with attachment using SMTP
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body text
        attachment_path: Path to file to attach
        filename: Name for the attached file
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    from_email = GeneralSettings.FROM_EMAIL
    app_password = GeneralSettings.MAIL_PASS_KEY

    # Create message container
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.add_header('Reply-To', from_email)

    # Attach body text
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Attach file
        with open(attachment_path, 'rb') as file:
            part = MIMEApplication(
                file.read(),
                Name=filename
            )
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(from_email, app_password)
            server.send_message(msg)
        
        return True

    except FileNotFoundError:
        print(f"[MAIL ERROR] Attachment file not found: {attachment_path}")
        return False
        
    except smtplib.SMTPException as e:
        print(f"[MAIL ERROR] SMTP error occurred: {str(e)}")
        return False
        
    except Exception as e:
        print(f"[MAIL ERROR] Unexpected error: {str(e)}")
        return False

# create a function to send email to all interns who have completed their internship
# parameters will be internship title, internship duration, and mails [list]
def send_internship_completion_email(mails, internship_title, internship_duration):
    message_body = f"""
Dear Intern,
We are pleased to inform you that the internship titled "{internship_title}" has been successfully completed.
Your contributions during the period of {internship_duration} is greatly appreciated.

We encourage you to keep in touch and stay connected with us for future opportunities.

You can check your internship status at https://www.nisc.co.in/internships/verify

!! Note !!
Your Profile will be moved to Completed Interns section, and you will not be able to login to the NISC Portal after this.
New Id will be created for new internship.

Thank you for your hard work and dedication.
Best regards,
NISC Team
"""

    subject = f"Internship Completion: {internship_title}"

    # create a thread for each email to be sent
    threads = []
    print(f"Sending internship completion email to {len(mails)} interns")
    for email in mails:
        thread = threading.Thread(target=send_email_to, args=(email, email, subject, message_body))
        threads.append(thread)
        thread.start()

    pass