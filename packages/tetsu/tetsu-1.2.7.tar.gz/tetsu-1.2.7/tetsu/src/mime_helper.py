# MIME Helper --- Send E-Mails VIA Python

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from tetsu.src.log_helper import logger

logger = logger(name=__name__, handler="console")


def send_df(df, filename, sender_email, receiver_email: list[str], subject):
    """
    Email a dataframe as a csv attachment
    :param df: pandas dataframe to send in email
    :param filename: file name that will be attached in email
    :param sender_email: email address sending mail
    :param receiver_email: email address receiving mail
    :param subject: email subject header
    """
    try:
        file = MIMEApplication(df.to_csv(index=False), Name=f"{filename}.csv")
        message = MIMEMultipart()

        smtp = "na.relay.ibm.com"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject
        message.attach(file)

        server = smtplib.SMTP(smtp, 25)
        server.sendmail(sender_email, receiver_email.split(","), message.as_string())
    except Exception as e:
        logger.exception(f"Could not send the dataframe as a CSV due to {e}")
    else:
        server.quit()
        logger.info(f"Dataframe sent to {receiver_email} successfully")


def send_file(
    file_path: str,
    file_name: str,
    file_type: str,
    sender_email: str,
    receiver_email: list[str],
    subject: str,
    message_body: str = None,
):
    """
    Email a file
    :param file_path: The path to the file that will be sent
    :param file_name: The name of the file once it is sent
    :param file_type: The type of file (xlsx, csv, etc...)
    :param sender_email: The senders email address
    :param receiver_email: The recipients email address
    :param subject: The subject header for the email
    :param message_body: The body of the message in the Email
    """
    try:
        message = MIMEMultipart()

        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject
        smtp = "na.relay.ibm.com"

        if message_body:
            body = MIMEText(_text=message_body, _subtype="html")
            message.attach(body)

        with open(file_path, "rb") as f:
            file_data = f.read()
            part = MIMEApplication(file_data, _subtype=file_type)
            part.add_header(
                _name="Content-Disposition", _value="attachment", filename=file_name
            )
            message.attach(part)

        server = smtplib.SMTP(smtp, port=25)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        logger.exception(f"Could not send {file_name} due to {e}")
    else:
        server.quit()
        logger.info(f"{file_name} sent to {receiver_email} successfully")


def send_message(sender_email, receiver_email, subject, message_body):
    """
    Email a message with no attachments
    :param sender_email: email address sending mail
    :param receiver_email: email address receiving mail
    :param subject: email subject header
    :param message_body: Body of message that you want to send
    """
    try:
        message = MIMEMultipart()

        # Create a multipart message and set headers
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        smtp = "na.relay.ibm.com"

        body = MIMEText(message_body)
        message.attach(body)

        server = smtplib.SMTP(host=smtp, port=25)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        logger.exception(f"Could not send email to {receiver_email} due to {e}")
    else:
        server.quit()
        logger.info(f"Email sent to {receiver_email} successfully")
