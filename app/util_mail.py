import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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