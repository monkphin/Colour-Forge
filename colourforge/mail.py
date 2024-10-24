from flask_mail import Message
from flask import render_template

from colourforge import mail


def welcome_email(email_address, username):
    """
    Sends a welcome email to a new user who has registered an account.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.


    Returns:
        None
    """
    msg = Message(
        subject="Welcome to ColourForge",
        sender="noreply@colourforge.co.uk",
        recipients=[email_address]
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
    msg.html = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>Welcome to Colourforge</p>
            <p>Thank you for registering an account with us.</p>
            <p>Don't worry, we just use your email for account messages like
            password resets and will not spam you!</p>
            <p>Thanks,<br>
            The Colourforge Team</>
        </body>
    </html>
    """

    mail.send(msg)


def account_deletion(email_address, username):
    """
    Sends a confirmation email to a user who deletes their account.

    Parameters:
        username (str): The username of the recipient.
        email_address (str): The email address of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your account has been deleted.",
        sender="noreply@colourforge.co.uk",
        recipients=[email_address]
    )

    # Plain text body
    msg.body = f"""
    Hey {username},

    Sorry to see you go.
    Your account has been successfully deleted.

    Thanks,
    The Colourforge Team
    """

    # HTML Email
    msg.html = f"""
    <html>
        <body>
            <p>Hey {username},</p>
            <p>Sorry to see you go</p>
            <p>Your account has been successfully deleted.</p>
            <p>Thanks,<br>
            The Colourforge Team</>
        </body>
    </html>
    """

    mail.send(msg)


def password_change(email_address, username):
    """
    Sends a confirmation email to a user who changes their password.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your password has been changed.",
        sender="noreply@colourforge.co.uk",
        recipients=[email_address]
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
    msg.html = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>We wanted to inform you that your password was successfully
            changed.</p>
            <p>If you initiated this change, no further action is needed. If
            you did not request a password change, please contact us
            immediately using the link below to secure your account:</p>
            <p>
              <a href="https://colourforge.co.uk/contact">Contact Support</a>
            </p>
            <p>Thanks,<br>
            The Colourforge Team</p>
        </body>
    </html>
    """

    mail.send(msg)


def email_change(email_address, old_email, username):
    """
    Sends a confirmation email to a user who has changed their email address.

    Parameters:
        email_address (str): The email address of the recipient.
        username (str): The username of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Your email has been changed.",
        sender="noreply@colourforge.co.uk",
        recipients=[email_address, old_email]
    )

    # Plain text body
    msg.body = f"""
    Hey {username}

    We wanted to inform you that your email was successfully changed.

    Thanks,
    The ColourForge Team
    """

    # HTML Email
    msg.html = f"""
    <html>
       <body>
            <p>Hi {username},</p>
            <p>We wanted to inform you that your email was successfully
            changed</p>
            <p>Thanks,<br>
            The Colourforge Team</>
        </body>
    </html>

    """

    mail.send(msg)


def contact_form(sender_email, sender_name, subject, message_content):
    """
    Sends the content of a contact form.

    Parameters:
        sender_email (str): The email address of the sender.
        sender_name (str): The name of the user from the form.
        subject (str): The subject of the message.
        message_content (str): The content of the form that the user submitted.

    Returns:
        None
    """
    msg = Message(
        sender="noreply@colourforge.co.uk",
        recipients=["darren.burrows@colourforge.co.uk"],
        subject=subject,
        reply_to=sender_email
    )

    # Plain text body
    msg.body = f"{sender_name} has submitted an email:\n\n{message_content}"

    # HTML Email
    msg.html = render_template("form_email.html", sender_name=sender_name, message_content=message_content)
    
    f"""
    <html>
        <body>
            <p>{ sender_name } has submitted an email</p>
            <p>{ message_content }</p>
        </body>
    </html>
    """

    mail.send(msg)
