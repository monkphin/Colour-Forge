"""
Module: email_notifications.py

Description:
------------
This module handles the sending of various email notifications within the
Colourforge application. It utilizes Flask-Mail to send emails for user
registration, account deletion, password changes, email changes, and contact
form submissions. Each function is responsible for composing and sending a
specific type of email, ensuring consistent communication with users.

Functions:
----------
- welcome_email(email_address, username):
    Sends a welcome email to a new user upon successful registration.

- account_deletion(email_address, username):
    Sends a confirmation email to a user after their account has been deleted.

- password_change(email_address, username):
    Sends a notification email to a user after their password has been changed.

- email_change(email_address, old_email, username):
    Sends a confirmation email to a user after their email address has been
    changed.

- contact_form(sender_email, sender_name, subject, message_content):
    Sends the content of a contact form submitted by a user to the site
    administrator.
"""


from flask_mail import Message
from flask import render_template

from colourforge import mail


def welcome_email(email_address, username):
    """
    Sends a welcome email to a user who has successfully registered an account.
    The email includes both plain text and HTML to ensure maximum compatibility
    with a range of mail clients.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Welcome to ColourForge",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username},

    Welcome to Colourforge!

    Thank you for registering an account with us!

    Don't worry, we just use your email for account messages like password
    resets and will not spam you.
    We hate spam and junk emails as much as you do.

    Thanks,
    The Colourforge Team
    """

    # HTML Email
    msg.html = render_template("emails/welcome.html", username=username)

    mail.send(msg)


def account_deletion(email_address, username):
    """
    Sends a confirmation email to a user after their account has been
    successfully deleted. This serves as a record of the account deletion to
    confirm that we have done as the user requested.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your account has been deleted.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username},

    Sorry to see you go.
    Your account and all associated data have been successfully deleted.

    Thanks,
    The Colourforge Team
    """

    # HTML Email
    msg.html = render_template(
        "emails/account_deletion.html",
        username=username
    )

    mail.send(msg)



def admin_account_deletion(email_address, username):
    """
    Sends a confirmation email to a user after an admin deletes their account.
    This serves as a record of the account deletion to let the user know their
    account has been deleted. 

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your account has been deleted.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username},

    Unfortunately we have had to delete your account, either at your request
    or due to an issue with your usage of the site or your account. 
    Your account and all associated data have been deleted

    Thanks,
    The Colourforge Team
    """

    # HTML Email
    msg.html = render_template(
        "emails/admin_account_deletion.html",
        username=username
    )

    mail.send(msg)


def password_change(email_address, username):
    """
    Sends an email to notify the user that their password has been successfully
    changed.
    If the user did not initiate the change, they are advised to contact
    support immediately.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your password has been changed.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username}

    We wanted to inform you that your password was successfully changed.

    If you initiated this change, no further action is needed. If you did not
    request a password change, please contact us using
    https://colourforge.co.uk/contact immediately to secure your account.

    Thanks,
    The ColourForge Team
    """

    # HTML Email
    msg.html = render_template(
        "emails/password_change.html",
        username=username
    )

    mail.send(msg)


def admin_password_change(email_address, username):
    """
    Sends an email to notify the user that their password has been successfully
    changed.
    If the user did not initiate the change, they are advised to contact
    support immediately.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your password has been changed.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username}

    We wanted to inform you that your password was changed by an admin.

    If you requested this change, no further action is needed and the admin
    will be in touch with your new password shortly. 
    If you did not request a password change, please contact us using
    https://colourforge.co.uk/contact immediately to secure your account.

    Thanks,
    The ColourForge Team
    """

    # HTML Email
    msg.html = render_template(
        "emails/admin_password_change.html",
        username=username
    )

    mail.send(msg)


def email_change(email_address, old_email, username):
    """
    Sends a confirmation email to notify the user that their email address has
    been successfully changed.
    The email is sent to both the new and old email addresses to ensure
    security.

    Parameters:
        email_address (str): The new email address of the recipient.
        old_email (str): The previous email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your email has been changed.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username}

    We wanted to inform you that your email was successfully changed.
    If you did not request this change, please contact us
    immediately using the link below to secure your account:
    https://colourforge.co.uk/contact immediately to secure your account.

    Thanks,
    The ColourForge Team
    """

    # HTML Email
    msg.html = render_template("emails/email_change.html", username=username)

    mail.send(msg)


def admin_email_change(email_address, old_email, username):
    """
    Sends a confirmation email to notify the user that their email address has
    been successfully changed by an admin. 
    The email is sent to both the new and old email addresses to ensure
    security.

    Parameters:
        email_address (str): The new email address of the recipient.
        old_email (str): The previous email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your email has been changed.",
        sender="Colour Forge",
        recipients=[email_address],
        reply_to='noreply@colourforge.co.uk'
    )

    # Plain text body
    msg.body = f"""
    Hey {username}

    We wanted to inform you that your email was successfully changed by an
    admin.
    If you did not request this change, please contact us immediately using
    the link below to secure your account:
    https://colourforge.co.uk/contact immediately to secure your account.

    Thanks,
    The ColourForge Team
    """

    # HTML Email
    msg.html = render_template("emails/admin_email_change.html", username=username)

    mail.send(msg)


def contact_form(sender_email, sender_name, subject, message_content):
    """
    Send a Contact Form Submission Email to the Administrator.

    Sends the content of a contact form submitted by a user to the site
    administrator.
    The email includes both plain text and HTML versions of the message for
    better readability.

    Parameters:
        sender_email (str): The email address of the sender.
        sender_name (str): The name of the user submitting the form.
        subject (str): The subject of the message.
        message_content (str): The content of the message submitted by the
        user.

    Returns:
        None
    """
    msg = Message(
        sender="Colour Forge",
        recipients=["noreply@colourforge.co.uk"],
        subject=subject,
        reply_to=sender_email
    )

    # Plain text body
    msg.body = f"{sender_name} has submitted an email:\n\n{message_content}"

    # HTML Email
    msg.html = render_template(
        "emails/form_email.html",
        sender_name=sender_name,
        message_content=message_content
    )

    mail.send(msg)
