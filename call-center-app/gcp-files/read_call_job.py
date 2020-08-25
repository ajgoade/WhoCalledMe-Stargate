from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
# from t1 import ttest
# from transcribe_job import create_job
from datetime import datetime
import threading
# from get_transcript import get_job_status
# from pydub import AudioSegment
import io
import os
import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
#uncomment to debug - import pdb
# from google.cloud import storage

global mediafileurl
global mediaformat
global jobname
secure-connect = ''

def mp3_to_wav(audio_file_name):
    #Not currently used
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")


def stereo_to_mono(audio_file_name):
    #Not currently used
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def frame_rate_channel(audio_file_name):
    #Not currently used
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels


def google_transcribe(audio_file_name, call_id):
   
    gcs_uri = audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        language_code='en-US')
        
    print("Submitting transcribe job .....")
    
    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    #Uncomment to debug - pdb.set_trace()
    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    print("Writing transcript results .....\n")
    cloud_config = {'secure_connect_bundle': secure-connect}
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.execute(f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s, transcript=%s where call_id={call_id}', (datetime.utcnow(), 'complete', transcript))

    session.shutdown()


def get_transactions():
    # Connect to Astra and Run query
    print("Connecting to DataStax Astra .....")
    cloud_config = {
        'secure_connect_bundle': secure-connect
    }
    auth_provider = PlainTextAuthProvider('callcenter', 'datastax')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()

    # Load records to be processed
    print("Reading Data from Astra .....")
    rows = session.execute(
        "select call_id, call_link from callcenter.call_center_voice_source where process_status='new'")
    
    #Create thread for each transcribe job        
    for row in rows:
        mediafileurl = row.call_link
        jobid = row.call_id

        threading.Thread(target=google_transcribe,args=(mediafileurl, jobid)).start()

        print("Job scheduled........")
        session.execute(f'update callcenter.call_center_voice_source set last_updated=%s, process_status=%s where call_id={jobid}',(datetime.utcnow(),'scheduled'))
    
    session.shutdown()


def main():
    import argparse
    global secure-connect

    parser = argparse.ArgumentParser()
    parser.add_argument("--secure_connect", type=str, default="./secure-connect-gcp.zip")
    args = parser.parse_args()
    secure-connect = args.secure_connect
    
    while True:
        get_transactions()
        print("Waiting 60.....")
        time.sleep(60)


if __name__ == "__main__":
    main()
