from flask_mail import Message
import traceback

from colourforge import mail

def welcome_email(email_address):
    """
    Sends a welcome email to a new user who has registered an account.

    Parameters:
        email_address (str): The email address of the recipient.

    Returns:
        None
    """
    msg = Message(
        subject="Welcome to ColourForge",
        sender="noreply@colourforge.co.uk",
        recipients=[email_address]
    )

    # Plain text body
    msg.body = """Welcome to Colourforge
    
Thank you for registering an account with us!

Don't worry, we just use your email for account messages like password resets and will not spam you.
We hate spam and junk emails as much as you do. 

Visit our website: https://colourforge.co.uk
"""

    # HTML Email
    msg.html = """
    <html>
        <body>
            <h1>Welcome to Colourforge</h1>
            <p>Thank you for registering an account with us.</p> 
            <p>Don't worry, we just use your email for account messages like password resets and will not spam you!</p>
            <p><a href="https://colourforge.co.uk">Visit our Website</a></p>
        </body>
    </html>            
    """

    mail.send(msg)



def account_deletion(email_address):
    """
    Sends a confirmation email to a user who deletes their account.

    Parameters:
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
    msg.body = "Sorry to see you go.\n\nYour account has been successfully deleted."


    # HTML Email
    msg.html = """
    <html>
        <body>
            <h1>Sorry to see you go</h1>
            <p>Your account has been successfully deleted.</p>
        </body>
    </html>            
    """

    mail.send(msg)


def contact_form(sender_email, sender_name, subject, message_content):
    """
    Sends the content of a contact form.

    Parameters:
        email_address (str): The email address of the recipient.
        sender_name (str): The name of the user from the form
        message_content (str): The content of the form that the user submitted. 
        
    Returns:
        None
    """
    msg = Message(
        sender="noreply@colourforge.co.uk",
        recipients=["darren.burrows@colourforge.co.uk"],
        subject=subject, 
        reply_to=sender_email #Using this due to Googles SMTP server only allowing specific emails to send. 
    )

    # Plain text body
    msg.body = f"{sender_name} has submitted an email:\n\n{message_content}"


    # HTML Email
    msg.html = f"""
    <html>
        <body>
            <p>{ sender_name } has submitted an email</p>
            <p>{ message_content }</p>
        </body>
    </html>            
    """

    mail.send(msg)