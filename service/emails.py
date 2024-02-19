import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from conf.secret import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT


def send_email(subject, message, to_email):
    """
    The send_email function sends an email to the user with a link to reset their password.

    :param subject: Set the subject of the email
    :param message: Pass the message that will be sent to the user
    :param to_email: Specify the email address of the recipient
    :return: None
    :doc-author: Trelent
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Enable security
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)  # Login to the server
        text = msg.as_string()
        print(text)
        server.sendmail(EMAIL_HOST_USER, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
