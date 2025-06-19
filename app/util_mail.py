import smtplib
# from email.mime.text import MIMEText

# def send_email(to_email, subject, message_body):
#     from_email = 'nisc.co.in@gmail.com'
#     app_password = 'gtdl lscl nnhi jiwa'

#     # Create the email message
#     msg = MIMEText(message_body)
#     msg['Subject'] = subject
#     msg['From'] = from_email
#     msg['To'] = to_email

#     try:
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(from_email, app_password)
#             server.send_message(msg)
#         return True
#     except Exception as e:
#         return False


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(name, to_email, subject, message_body):
    from_email = 'nisc.co.in@gmail.com'
    app_password = 'gtdl lscl nnhi jiwa'

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
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


