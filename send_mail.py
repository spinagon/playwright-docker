from datetime import datetime
import select
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os

# Email credentials and details
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")


def send_mail(address=receiver_email, subject="", body="", attachments=()):
    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = address
    for att in attachments:
        attach(msg, att)
    msg.attach(MIMEText(body, "html"))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {repr(e)}")


def attach(msg, att):
    ctype, encoding = mimetypes.guess_type(att)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        with open(att) as f:
            attachment = MIMEText(f.read(), _subtype=subtype)
    elif maintype == "image":
        with open(att, "rb") as f:
            attachment = MIMEImage(f.read(), _subtype=subtype)
    elif maintype == "audio":
        with open(att, "rb") as f:
            attachment = MIMEAudio(f.read(), _subtype=subtype)
    else:
        with open(att, "rb") as f:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=att)
    attachment.add_header("Content-ID", f"<{att}>")
    msg.attach(attachment)


if __name__ == "__main__":
    import sys

    if select.select(
        [
            sys.stdin,
        ],
        [],
        [],
        0.2,
    )[0]:
        body = sys.stdin.read()
    else:
        body = ""
    attachments = sys.argv[1:]
    send_mail(subject=datetime.now().ctime(), body=body, attachments=attachments)
