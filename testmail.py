from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'noreply@colourforge.co.uk'  # Use your actual Gmail address
app.config['MAIL_PASSWORD'] = 'xzkk wzok athw ydhp'     # Use your generated App Password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

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