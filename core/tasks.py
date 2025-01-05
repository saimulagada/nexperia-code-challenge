from celery import shared_task
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import send_mail
from django.conf import settings
import time

@shared_task
def send_email_with_delay(first_name, last_name, subject, body, recipient_email, delay_seconds):
    try:
        # Delay the email sending
        time.sleep(delay_seconds)  # Delay before sending the email

        # Format the email content
        formatted_body = f"Dear {first_name} {last_name},\n\n{body}"

        # Set up the MIME (Multipurpose Internet Mail Extensions) for the email
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER  # Your Gmail email address (configured in settings.py)
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(formatted_body, 'plain'))

        # Establish a secure SMTP connection with Gmail's server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # Login to the Gmail account (this needs to be the email configured in settings.py)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Send the email
            server.sendmail(settings.EMAIL_HOST_USER, recipient_email, msg.as_string())

        return f"Email sent to {recipient_email} successfully after {delay_seconds} seconds."

    except smtplib.SMTPException as e:
        return f"Failed to send email to {recipient_email}: {str(e)}"
