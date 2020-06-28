import os
from flask import Flask, request, render_template

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Go get the values from .env file
from dotenv import load_dotenv
load_dotenv()

import http.client, urllib.request, urllib.parse, urllib.error, base64

# Load the values from environmental variables
# The magic of dotenv
COGSVCS_KEY = os.getenv('COGSVCS_KEY')
COGSVCS_CLIENTURL = os.getenv('COGSVCS_CLIENTURL')

# Create the core Flask app
app = Flask(__name__)

@app.route('/dog', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # User is requesting the form
        return render_template('form.html')
    elif request.method == 'POST':
        # User has sent us data
        image = request.files['image']
        client = ComputerVisionClient(COGSVCS_CLIENTURL, CognitiveServicesCredentials(COGSVCS_KEY))
        result = client.describe_image_in_stream(image)
        message = 'No dog found. How sad. :-('
        if 'dog' in result.tags:
            message = 'There is a dog! Wonderful!!'
        return render_template('result.html', message=message)



@app.route('/insights', methods=['GET'])
def insights():
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '03bbf7eb125c42c5be971affc2544666',
    }

    try:
        conn = http.client.HTTPSConnection('api.videoindexer.ai')
        conn.request("GET", "/trial/Accounts/0862fd32-a58c-4afd-ab7d-b76f96a268c7/Videos/f865b7c156/InsightsWidget", "", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print(e)

    if __name__ == "__main__":
        app.run(port = 8000, debug = True)
