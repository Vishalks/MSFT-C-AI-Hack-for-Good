import json
import os
import http.client, urllib.request, urllib.parse, urllib.error, base64
import string
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
load_dotenv()

from markupsafe import escape

printable = set(string.printable)

# Load the values from environmental variables
# The magic of dotenv
COGSVCS_KEY = os.getenv('COGSVCS_KEY')
COGSVCS_CLIENTURL = os.getenv('COGSVCS_CLIENTURL')

ta_credential = CognitiveServicesCredentials(COGSVCS_KEY)
search_client = WebSearchClient(
    endpoint=COGSVCS_CLIENTURL, credentials=ta_credential)


app = Flask(__name__)

file_to_read = json.load(open('holovid.json',encoding='utf8'))
insights = file_to_read['summarizedInsights']
video = file_to_read['videos']


# @app.route('/getkeywords',  methods=['GET'])
def getkeywords(max_keywords=5, max_results=5):

    keywords = {}
    for ind, insight in enumerate(insights['keywords']):

        if ind >= max_keywords:
            break

        keyword = insight['name']
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

def getnamedentity(max_num=5):
    people = insights['namedPeople']

    output = []
    for ind, topic in enumerate(people):
        output.append({
            'name': topic['name'],
            'url': topic['referenceUrl']
        })
        if ind > max_num:
            break

    locations = insights['namedLocations']
    for ind, topic in enumerate(locations):
        output.append({
            'name': topic['name'],
            'url': topic['referenceUrl']
        })
        if ind > max_num:
            break


    return output



@app.route('/',  methods=['GET'])
def index():
    output_dict = getkeywords()
    out_trans = gettranscript()

    topics = gettopics()
    named_entities = getnamedentity()

    return render_template('result.html', 
        results=output_dict, transcripts=out_trans,
        named_entities=named_entities, topics=topics
    )

@app.route('/qa',  methods=['POST', 'GET'])
def qna_answer(question = "Please describe MasterCred"):
    headers = {
        # Request headers
        'Authorization': '0aeb1880-501f-4bb8-b73e-96f96d1cd329',
        'Content-type': 'application/json'
    }
 
    try:
        json_question = {'question':request.form['question']}
        json_data = json.dumps(json_question)
        conn = http.client.HTTPSConnection('video-analyzer.azurewebsites.net')
        
        print(question)

        conn.request(
            "POST", 
            "/qnamaker/knowledgebases/6123d042-c877-458d-8770-2feb34da05b3/generateAnswer",
            json_data,
            headers
        )

        response = conn.getresponse()
        data = response.read().decode()
        loaded_json = json.loads(data)
        answers_json = loaded_json['answers'][0]
        answer = answers_json['answer']
        score = answers_json['score']
        conn.close()
        answer = answer.encode("ascii", errors="ignore").decode()
        return jsonify({
            'answer': answer,
            'score': score,
            'status': 'ok'
        })
    except Exception as e:
        return jsonify({
            'answer': 'NA',
            'score': '0',
            'status': 'not ok'
        })


if __name__ == "__main__":
    app.run(port=8000, debug=True)


