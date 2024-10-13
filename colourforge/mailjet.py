from mailjet_rest import Client
import os

# Check if env.py exists and import it
if os.path.exists("../env.py"):
    import sys
    sys.path.append("..")
    import env  # This will set the environment variables


api_key = os.environ.get('MJ_APIKEY_PUBLIC')
api_secret = os.environ.get('MJ_APIKEY_PRIVATE')

mailjet = Client(auth=(api_key, api_secret))

data = {
    'FromEmail': 'noreply@colourforge.co.uk',
    'FromName': 'Colour Forge',
    'Subject': 'Your email flight plan!',
    'Text-part': 'Dear passenger, welcome to Mailjet! May the delivery force be with you!',
    'Html-part': '<h3>Dear passenger, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!<br />May the delivery force be with you!',
    'Recipients': [{'Email': 'darren.burrows@gmail.com'}]
}

result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())