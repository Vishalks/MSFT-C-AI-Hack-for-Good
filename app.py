import json
import os
# from azure.ai.textanalytics import TextAnalyticsClient
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


# @app.route('/getkeywords',  methods=['GET'])
def getkeywords(max_keywords=5, max_results=5):

    keywords = {}
    for ind, insight in enumerate(insights['keywords']):

        if ind >= max_keywords:
            break

        keyword = insight['name']
        # keywords[keyword] = {}
        # keywords[keyword]['appearances'] = insight['appearances']
        keywords[keyword] = []

        web_data = search_client.web.search(query=keyword)

        if hasattr(web_data.web_pages, 'value'):

            for _ in range(min(max_results, len(web_data.web_pages.value))):
                web_page = web_data.web_pages.value[_]
                temp = {}
                temp['name'] = web_page.name
                temp['url'] = web_page.url
                keywords[keyword].append(temp)

    return keywords
    # return render_template('result.html', keywords=keywords)


# @app.route('/gettranscript',  methods=['GET'])
def gettranscript(max_keywords=5, max_results=5):

    transcript = video[0]['insights']['transcript']
    new_transcript = []
    for tr in transcript:

        new_transcript.append({
            'text': tr['text'],
            'start': tr['instances'][0]['start'],
            'end': tr['instances'][0]['end']
        })

    # return render_template('result.html', transcript=new_transcript)
    return new_transcript

def gettopics(max_topics=5):

    topics = insights['topics']
    output = []
    for ind, topic in enumerate(topics):
        output.append({
            'name': topic['name'],
            'url': topic['referenceUrl']
        })
        if ind > max_topics:
            break

    return output

def getnamedpeople(max_num=5):
    people = insights['namedPeople']

    output = []
    for ind, topic in enumerate(people):
        output.append({
            'name': topic['name'],
            'url': topic['referenceUrl']
        })
        if ind > max_num:
            break

    return output



@app.route('/',  methods=['GET'])
def index():
    # with open('results.json') as file_ptr:
    #     results = json.load(file_ptr)
    #     output_dict = {}
    #     for keyword in results:
    #         output_dict[keyword] = results[keyword]['searchresults']

    # print(output_dict)
    # print(getkeywords())
    output_dict = getkeywords()

    # with open('transcripts.json') as file_ptr:
    #     transcripts = json.load(file_ptr)
    #     # print(transcripts)
    #     out_trans = []
    #     for transcript_id, transcript_details in transcripts.items():
    #         out_trans.append({
    #             'text': transcript_details['text'],
    #             'start': transcript_details['instances'][0]['start'],
    #             'end': transcript_details['instances'][0]['end'],
    #             }
    #         )

    # print(out_trans)
    out_trans = gettranscript()



    return render_template('result.html', results=output_dict, transcripts=out_trans)


if __name__ == "__main__":
    # keywords = getkeywords()
    # print(keywords)
    # gettranscript()
    # index()
    # print(gettopics())
    # print(getnamedpeople())
    # print(gettranscript())
    app.run(port=8000, debug=True)
