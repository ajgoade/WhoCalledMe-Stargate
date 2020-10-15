import threading
import time
from datetime import datetime
from os import environ

import requests              # for making REST API requests
import json                  # for converting json payloads to strings
import uuid                  # to create UUIDs for Astra connections

cloudlocation = ''
AUTH_UUID = str(uuid.uuid1())
USER = ''
PASSWORD = ''
DB_ID = ''
REGION = ''
BASE_URL = ''
NAMESPACE = 'callcenter'
COLLECTION = 'calls'
DOC_ROOT_PATH = f"/api/rest/v2/namespaces/{NAMESPACE}/collections/{COLLECTION}/"
TOKEN = ''
HEADERS = ''
stargate_client = ''


class Client:
    """
    An API Client for connecting to Stargate
    """

    def __init__(self, base_url, access_token, headers):
        self.base_url = base_url
        self.access_token = access_token
        self.headers = headers

    def post(self, payload={}, path=""):
        """
            Via the requests library, performs a post with the payload to the path
        """
        return requests.post(self.base_url + path,
                             data=json.dumps(payload),
                             headers=self.headers)

    def put(self, payload={}, path=""):
        """
            Via the requests library, performs a put with the payload to the path
        """
        return requests.put(self.base_url + path,
                            data=json.dumps(payload),
                            headers=self.headers)

    def patch(self, payload={}, path=""):
        """
            Via the requests library, performs a patch with the payload to the path
        """
        return requests.patch(self.base_url + path,
                              data=json.dumps(payload),
                              headers=self.headers)

    def get(self, payload={}, path=""):
        """
            Via the requests library, performs a get with the payload to the path
        """
        return requests.get(self.base_url + path,
                            data=json.dumps(payload),
                            headers=self.headers)

    def delete(self, payload={}, path=""):
        """
            Via the requests library, performs a delete with the payload to the path
        """
        return requests.delete(self.base_url + path,
                               data=json.dumps(payload),
                               headers=self.headers)

def authenticate(path="/api/rest/v1/auth"):
    """
        This convenience function uses the v1 auth REST API to get an access token
        returns: an auth token; 30 minute expiration
    """
    url = BASE_URL + path # we still have to auth with the v1 API
    payload = {"username": USER,
               "password": PASSWORD}
    headers = {'accept': '*/*',
               'content-type': 'application/json',
               'x-cassandra-request-id': AUTH_UUID}
    # make auth request to Astra
    r = requests.post(url,
                      data=json.dumps(payload),
                      headers=headers)
    # raise any authentication errror
    if r.status_code != 201:
        raise Exception(r.text)
    # extract and return the auth token
    data = json.loads(r.text)
    return data["authToken"]

def initialize_stargate():
    global stargate_client
    TOKEN = authenticate()
    HEADERS = {'content-type': 'application/json',
               'x-cassandra-token': TOKEN}
    stargate_client = Client(BASE_URL, TOKEN, HEADERS)

def google_transcribe(audio_file_name, jobid):
    from google.cloud import speech
    from google.cloud.speech import types

    gcs_uri = audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        language_code='en-US')

    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    for result in response.results:
        transcript += result.alternatives[0].transcript

    stargate_client.patch({"lastUpdated":int(time.time()),
                         "transcript":transcript,
                         "processStatus":"gcp_sentiment_needed"},
                        DOC_ROOT_PATH + jobid)

    threading.Thread(target=google_sentiment, args=(jobid, transcript)).start()

def google_sentiment(jobid, transcript):
    from google.cloud import language
    from google.cloud.language import enums
    from google.cloud.language import types

    client = language.LanguageServiceClient()

    document = types.Document(
        content=transcript,
        type=enums.Document.Type.PLAIN_TEXT)

    annotations = client.analyze_sentiment(document=document)

    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    final_sentiment = 'Overall Sentiment: score of {:+.2f} with magnitude of {:+.2f}'.format(
        score, magnitude)

    stargate_client.patch({"lastUpdated":int(time.time()),
                         "sentiment":final_sentiment,
                         "processStatus":"complete"},
                        DOC_ROOT_PATH + jobid)

def amazon_transcribe(audio_file_name, jobid):
    import boto3
    import requests

    aws_uri = audio_file_name
    transcript = ''
    jobname = str(jobid)+'_'+datetime.utcnow().strftime('%Y-%m-%d-%H.%M.%S.%f')[:-3]

    transcribe_client = boto3.client('transcribe',  region_name='us-east-1')
    transcribe_client.start_transcription_job(TranscriptionJobName=jobname, Media={'MediaFileUri': aws_uri},
                                       MediaFormat='wav', LanguageCode='en-US')

    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=jobname)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(10)

    response = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
    transcript = response['results']['transcripts'][0]['transcript']

    stargate_client.patch({"lastUpdated":int(time.time()),
                         "transcript":transcript,
                         "processStatus":"aws_sentiment_needed"},
                        DOC_ROOT_PATH + jobid)


    threading.Thread(target=amazon_sentiment, args=(jobid, transcript)).start()

def amazon_sentiment(jobid, transcript):
    import boto3

    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')

    results = comprehend.detect_sentiment(Text=transcript, LanguageCode='en')

    final_sentiment = 'Overall Sentiment is {}: Scores are Positive {:+.2f}, Negative {:+.2f}, Neutral {:+.2f}, and Mixed {:+.2f}'.format(
        results['Sentiment'], results['SentimentScore']['Positive'], results['SentimentScore']['Negative'], results['SentimentScore']['Neutral'], results['SentimentScore']['Mixed'])

    stargate_client.patch({"lastUpdated":int(time.time()),
                         "sentiment":final_sentiment,
                         "processStatus":"complete"},
                        DOC_ROOT_PATH + jobid)

def get_transactions():

    rows = stargate_client.get({}, DOC_ROOT_PATH+'?page-size=20&where={"processStatus": {"$eq": "new"}}')

    if rows.status_code == 200:

        results = json.loads(rows.text)

        for data, key in results.items():
            if (key is not None):
                for subdata, subkey in key.items():
                    jobid = subdata
                    mediafileurl = subkey['callLink']

                    if cloudlocation == 'gcp':
                        threading.Thread(target=google_transcribe, args=(mediafileurl, jobid)).start()
                        stargate_client.patch({"lastUpdated": int(time.time()),
                                               "processStatus": "gcp_transcribe_scheduled"},
                                              DOC_ROOT_PATH + jobid)

                    elif cloudlocation == 'aws':
                        threading.Thread(target=amazon_transcribe, args=(mediafileurl, jobid)).start()
                        stargate_client.patch({"lastUpdated": int(time.time()),
                                               "processStatus": "aws_transcribe_scheduled"},
                                              DOC_ROOT_PATH + jobid)

                    elif cloudlocation == 'azure':
                        print("wasbs not available yet")

    elif rows.status_code == 401:
        initialize_stargate()

def main():
    import argparse
    global USER, PASSWORD, DB_ID, REGION, cloudlocation, TOKEN, stargate_client, BASE_URL, HEADERS

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, required=True,
                        help="Astra user id")
    parser.add_argument("-p", "--password",type=str, required=True,
                        help="Astra password")
    parser.add_argument("--db_id", type=str, required=True,
                        help="Astra Database ID")
    parser.add_argument("--region", type=str, required=True,
                        help="Astra DB region")
    parser.add_argument("-i", "--interval", type=int, default=60,
                        help="Time to rest between processes")
    parser.add_argument("--cloud", type=str, default='gcp', choices=['gcp', 'aws', 'azure'],
                        help="Cloud provider app is running in: gcp (default), aws, azure")
    parser.add_argument("--creds", type=str,
                        help="Location of Cloud provider's connection package, if needed")

    args = parser.parse_args()
    USER = args.user
    PASSWORD = args.password
    DB_ID = args.db_id
    REGION = args.region
    waittime = args.interval
    cloudlocation = args.cloud
    BASE_URL = f"https://{DB_ID}-{REGION}.apps.astra.datastax.com"

    if args.creds is not None:
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.creds

    initialize_stargate()

    while True:
        get_transactions()
        time.sleep(waittime)

if __name__ == "__main__":
    main()
