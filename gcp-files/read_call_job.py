import threading
import time
from datetime import datetime
from os import environ
#Cassandra / Astra imports
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

secureconnect = ''
cloudlocation = ''



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

    #Astra connection properties
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, transcript=%s where call_id={jobid}',
        (datetime.utcnow(), 'gcp_sentiment_needed', transcript))

    threading.Thread(target=google_sentiment, args=(jobid, transcript)).start()

    session.shutdown()


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

    #Astra connection properties
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, sentiment=%s where call_id={jobid}',
        (datetime.utcnow(), 'gcp_complete', final_sentiment))
    session.shutdown()


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

    #Astra connection properties
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, transcript=%s where call_id={jobid}',
        (datetime.utcnow(), 'aws_sentiment_needed', transcript))

    threading.Thread(target=amazon_sentiment, args=(jobid, transcript)).start()

    session.shutdown()


def amazon_sentiment(jobid, transcript):
    import boto3

    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')

    results = comprehend.detect_sentiment(Text=transcript, LanguageCode='en')

    final_sentiment = 'Overall Sentiment is {}: Scores are Positive {:+.2f}, Negative {:+.2f}, Neutral {:+.2f}, and Mixed {:+.2f}'.format(
        results['Sentiment'], results['SentimentScore']['Positive'], results['SentimentScore']['Negative'], results['SentimentScore']['Neutral'], results['SentimentScore']['Mixed'])

    #Astra connection properties
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, sentiment=%s where call_id={jobid}',
        (datetime.utcnow(), 'complete', final_sentiment))
    session.shutdown()


def get_transactions():

    #Astra connection properties
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()

    rows = session.execute(
        "select call_id, call_link from callcenter.call_center_voice_source where process_status='new'")

    for row in rows:
        mediafileurl = row.call_link
        jobid = row.call_id

        if cloudlocation == 'gcp':
            threading.Thread(target=google_transcribe,args=(mediafileurl, jobid)).start()
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'gcp_transcribe_scheduled'))

        elif cloudlocation == 'aws':
            threading.Thread(target=amazon_transcribe, args=(mediafileurl, jobid)).start()
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'aws_transcribe_scheduled'))

        elif cloudlocation == 'azure':
            print("wasbs not available yet")
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'azure_unavailable'))

    session.shutdown()


def main():
    import argparse
    global secureconnect
    global cloudlocation

    parser = argparse.ArgumentParser()
    parser.add_argument("--secure_connect", type=str, required=True,
                        help="Location of Astra secure connect package")
    parser.add_argument("--creds",type=str,
                        help="Location of Cloud provider's connection package, if needed")
    parser.add_argument("--interval", type=int, default=60,
                        help="Interval to pause before checking for new transactions (default 60)")
    parser.add_argument("--cloud", type=str, default='gcp', choices=['gcp', 'aws', 'azure'],
                        help="Cloud provider app is running in: gcp (default), aws, azure")
    args = parser.parse_args()
    secureconnect = args.secure_connect
    waittime = args.interval
    cloudlocation = args.cloud

    if args.creds is not None:
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.creds

    while True:
        get_transactions()
        time.sleep(waittime)


if __name__ == "__main__":
    main()
