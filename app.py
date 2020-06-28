import json
import os
from azure.ai.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from flask import Flask, request, render_template

from dotenv import load_dotenv
load_dotenv()

# Load the values from environmental variables
# The magic of dotenv
COGSVCS_KEY = os.getenv('COGSVCS_KEY')
COGSVCS_CLIENTURL = os.getenv('COGSVCS_CLIENTURL')

ta_credential = CognitiveServicesCredentials(COGSVCS_KEY)
# cv_analytics_client = ComputerVisionClient(
#     endpoint=COGSVCS_CLIENTURL, credential=COGSVCS_KEY)
# text_analytics_client = TextAnalyticsClient(
#     endpoint=COGSVCS_CLIENTURL, credential=COGSVCS_KEY)
search_client = WebSearchClient(
    endpoint=COGSVCS_CLIENTURL, credentials=ta_credential)


app = Flask(__name__)

file_to_read = json.load(open('holovid.json'))
insights = file_to_read['summarizedInsights']
video = file_to_read['videos']


@app.route('/getkeywords',  methods=['GET'])
def getkeywords(max_keywords=5, max_results=5):

    keywords = {}
    for ind, insight in enumerate(insights['keywords']):

        if ind >= max_keywords:
            break

        keyword = insight['name']
        keywords[keyword] = {}
        keywords[keyword]['appearances'] = insight['appearances']
        keywords[keyword]['searchresults'] = []

        web_data = search_client.web.search(query=keyword)

        if hasattr(web_data.web_pages, 'value'):

            for _ in range(min(max_results, len(web_data.web_pages.value))):
                web_page = web_data.web_pages.value[_]
                temp = {}
                temp['name'] = web_page.name
                temp['url'] = web_page.url
                keywords[keyword]['searchresults'].append(temp)

    # return keywords
    return render_template('result.html', keywords=keywords)


@app.route('/gettranscript',  methods=['GET'])
def gettranscript(max_keywords=5, max_results=5):

    transcript = video[0]['insights']['transcript']
    new_transcript = {}
    for tr in transcript:
        new_transcript[str(tr["id"])] = tr

    return render_template('result.html', transcript=new_transcript)


if __name__ == "__main__":
    # keywords = getkeywords()
    # print(keywords)
    # gettranscript()
    # print(gettranscript())
    app.run(port=8000, debug=True)
