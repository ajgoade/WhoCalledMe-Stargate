FROM  python:latest
COPY read_call_job.py /
COPY fieldops-gce-presales-a5ec0edbb261.json /
COPY secure-connect-gcp.zip /
RUN pip install --upgrade google-cloud-speech google-cloud google-cloud-language cassandra-driver boto3 gimme-aws-creds okta
# secure_connect, creds  and cloud are all dependant on your environment
CMD python /read_call_job.py --secure_connect /secure-connect-gcp.zip --creds /fieldops-gce-presales-a5ec0edbb261.json --interval 10 --cloud gcp
