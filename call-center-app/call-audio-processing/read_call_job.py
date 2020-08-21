from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from t1 import ttest
from transcribe_job import create_job
from datetime import datetime
#from get_transcript import get_job_status

# Connect to Astra and Run query

print("Connecting to DataStax Astra ..... \n")
cloud_config= {
        'secure_connect_bundle': '/home/ec2-user/secure-connect-demo-db.zip'
}
auth_provider = PlainTextAuthProvider('david', 'qwerty')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

# loading data
print("Reading Data from Astra ..... \n")
row = session.execute("select * from demo_callcentre.call_centre_voice_source where process_status='New'")

mediafileurl = row[0].call_s3_link
mediaformat = row[0].call_audio_filetype
jobname = str(row[0].call_id)+"_job"
print(jobname)

# Create Job in AWS Transcribe
create_job(mediafileurl,mediaformat,jobname)

session.execute("insert into demo_callcentre.job_status ( job_id, last_update_time,status) values (%s, %s, %s)",(jobname,datetime.now(), "scheduled"))