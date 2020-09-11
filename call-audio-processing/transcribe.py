import boto3

session = boto3.Session(profile_name='fieldops')
transcribe = session.client('transcribe')

# transcribe job

def create_job(mediafileurl,mediaformat,jobname):
    response = transcribe.start_transcription_job( TranscriptionJobName=jobname, Media={'MediaFileUri': mediafileurl}, MediaFormat=mediaformat, LanguageCode="en-US", MediaSampleRateHertz=44100)
    return print(f"Request submitted: {response['ResponseMetadata']['RequestId']}")