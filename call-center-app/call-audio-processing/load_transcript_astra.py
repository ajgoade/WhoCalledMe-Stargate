from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import boto3
from datetime import datetime
import requests

# Connect to Astra and Run query

print("Connecting to DataStax Astra ..... \n")
cloud_config= {
        'secure_connect_bundle': '/home/ec2-user/secure-connect-demo-db.zip'
}
auth_provider = PlainTextAuthProvider('username', 'password')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

# loading data
print("Reading Data from Astra ..... \n")
row = session.execute("select * from demo_callcentre.job_status where status='scheduled'")
jobname = row[0].job_id

awssession = boto3.Session(profile_name='fieldops')
transcribe = awssession.client('transcribe')

while True:
    print(jobname)
    status = transcribe.get_transcription_job(TranscriptionJobName=jobname)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        end = datetime.now()
        break
    print("Not ready yet...")
    time.sleep(5)


response = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
transcript = response['results']['transcripts'][0]['transcript']

call_id = jobname.split("_")[0]
session.execute(f'update demo_callcentre.call_centre_voice_source set last_updated=%s, transcript=%s, process_status=%s where call_id={call_id}',(datetime.now(),transcript,'Processed'))

print("Job Processed")