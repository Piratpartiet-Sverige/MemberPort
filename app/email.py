import smtplib

from app.logger import logger
from email.message import EmailMessage
from app.config import Config


def send_email(to: str, subject: str, message: str, send_verification: bool = False, verify_link: str = ""):
    config = Config.get_config()

    username = config.get("Email", "username")
    password = config.get("Email", "password")
    smtp_server = config.get("Email", "smtp_server", fallback="")

    try:
        smtp_port = config.getint("Email", "smtp_port", fallback=0)
    except ValueError as exc:
        logger.debug(exc.__str__())
        logger.warning("Could not get a value for the SMTP Port, setting it to 0")
        smtp_port = 0

    if smtp_server == "" or smtp_port == 0:
        return

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = config.get("Email", "from")
    msg['To'] = to

    if send_verification is True and verify_link != "" and verify_link is not None:
        msg.set_content(message + "\nClick on the following link to confirm your e-mail address: " +
                        config.get("WebServer", "url") + verify_link)
    elif send_verification is True:
        logger.warning('"send_verification" was set to true but no link was provided')

    logger.debug("SMTP Server: " + smtp_server)
    logger.debug("SMTP Port: " + smtp_port.__str__())
    logger.debug("SMTP Username: " + username)

    try:
        s = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
        s.login(username, password)
        s.send_message(msg)
        s.quit()
    except smtplib.SMTPNotSupportedError as e:
        logger.warning("No login required to the SMTP server, " + e.__str__())
        s.send_message(msg)
        s.quit()
    except Exception as e:
        logger.warning("SMTP error: could not send mail, " + e.__str__())
