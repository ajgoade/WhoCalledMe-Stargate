#import pdb
import threading
import time
from datetime import datetime
# from pydub import AudioSegment
from os import environ
#Cassandra / Astra imports
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
#Google Cloud imports
from google.cloud import speech
from google.cloud.speech import types
# from google.cloud import storage
#Amazon imports
import boto3
import requests

global mediafileurl
global mediaformat
global jobname
secureconnect = ''
cloudlocation = ''

#def mp3_to_wav(audio_file_name):
    #Not currently used
#    if audio_file_name.split('.')[1] == 'mp3':
#        sound = AudioSegment.from_mp3(audio_file_name)
#        audio_file_name = audio_file_name.split('.')[0] + '.wav'
#        sound.export(audio_file_name, format="wav")


#def stereo_to_mono(audio_file_name):
    #Not currently used
#    sound = AudioSegment.from_wav(audio_file_name)
#    sound = sound.set_channels(1)
#    sound.export(audio_file_name, format="wav")


#def frame_rate_channel(audio_file_name):
    #Not currently used
#    with wave.open(audio_file_name, "rb") as wave_file:
#        frame_rate = wave_file.getframerate()
#        channels = wave_file.getnchannels()
#        return frame_rate, channels


def google_transcribe(audio_file_name, jobid):
   
    gcs_uri = audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        language_code='en-US')
        
    #print("Submitting transcribe job "+str(jobid)+" .....")
    
    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    #Uncomment to debug - pdb.set_trace()
    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    #print("Writing transcript results for "+str(jobid)+" .....")
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, transcript=%s where call_id={jobid}', (datetime.utcnow(), 'sentiment_needed', transcript))

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

    # print("Writing transcript results for "+str(jobid)+" .....")
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, sentiment=%s where call_id={jobid}',
        (datetime.utcnow(), 'complete', final_sentiment))

    session.shutdown()


def amazon_transcribe(audio_file_name, jobid):
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
        #print("Not ready yet...")
        time.sleep(10)
    #print(status)

    response = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
    transcript = response['results']['transcripts'][0]['transcript']

    # print("Writing transcript results for "+str(jobid)+" .....")
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, transcript=%s where call_id={jobid}',
        (datetime.utcnow(), 'aws_complete', transcript))

    #threading.Thread(target=amazon_sentiment, args=(jobid, transcript)).start()

    session.shutdown()


def amazon_sentiment(jobid, transcript):
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

    # print("Writing transcript results for "+str(jobid)+" .....")
    cloud_config = {'secure_connect_bundle': secureconnect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(
        f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, sentiment=%s where call_id={jobid}',
        (datetime.utcnow(), 'complete', final_sentiment))

    session.shutdown()


def get_transactions():
    # Connect to Astra and Run query
    #print("Connecting to DataStax Astra .....")
    cloud_config = {
        'secure_connect_bundle': secureconnect
    }
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()

    # Load records to be transcribed
    #print("Reading Data from Astra .....")
    rows = session.execute(
        "select call_id, call_link from callcenter.call_center_voice_source where process_status='new'")
    
    #Create thread for each transcribe job        
    for row in rows:
        mediafileurl = row.call_link
        jobid = row.call_id

        if cloudlocation == 'gcp':
            threading.Thread(target=google_transcribe,args=(mediafileurl, jobid)).start()
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'transcribe_scheduled'))

        elif cloudlocation == 'aws':
            threading.Thread(target=amazon_transcribe, args=(mediafileurl, jobid)).start()
            #print("s3 not available yet")
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'transcribe_scheduled'))

        elif cloudlocation == 'azure':
            print("wasbs not available yet")
            session.execute(
                f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',
                (datetime.utcnow(), 'azure_unavailable'))

        #print("Job scheduled "+str(jobid)+" .....")

    session.shutdown()


def main():
    import argparse
    global secureconnect
    global cloudlocation

    #pdb.set_trace()
    parser = argparse.ArgumentParser()
    parser.add_argument("--secure_connect", type=str, default="./secure-connect-gcp.zip",
                        help="Location of Astra secure connect package")
    parser.add_argument("--creds",type=str,
                        help="Location of Cloud providor's connection package")
    parser.add_argument("--interval", type=int, default=60,
                        help="Interval to pause before checking for new transactions")
    parser.add_argument("--cloud", type=str, default='gcp',
                        help="Cloud provider app is running in: gcp (default), aws, azure")
    args = parser.parse_args()
    secureconnect = args.secure_connect
    waittime = args.interval
    cloudlocation = args.cloud

    if args.creds is not None:
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.creds

    while True:
        get_transactions()
        #print("Waiting "+str(waittime)+".....")
        time.sleep(waittime)


if __name__ == "__main__":
    main()
