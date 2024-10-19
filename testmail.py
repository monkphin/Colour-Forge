from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)


@app.route("/")
def index():
    msg = Message(
        subject='Hello from the other side!', 
        sender='noreply@colourforge.co.uk',  # Ensure this matches MAIL_USERNAME
        recipients=['darren.burrows@gmail.com']  # Replace with actual recipient's email
    )
    msg.body = "Hey, sending you this email from my Flask app, let me know if it works."
    mail.send(msg)
    return "Message sent!"

if __name__ == '__main__':
    app.run(debug=True)