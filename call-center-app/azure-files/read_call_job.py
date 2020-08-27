#!/usr/bin/env python
# coding: utf-8
from typing import List

import logging
import sys
import requests
import time
import json
import swagger_client as cris_client
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider



logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

# edit astra credentials below and keyspace
print("Connecting to DataStax Astra ..... \n")
cloud_config= {
        'secure_connect_bundle': '/Users/omer.saeed/dsapps/astra/secure-connect-osaeed-test.zip'
}
auth_provider = PlainTextAuthProvider('osaeed', 'cassandra123')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()
ASTRA_KEYSPACE = 'osaeed_ks'


# Edit subscription key and region for the Azure speech service
SUBSCRIPTION_KEY = "5bc0d7b285254e0eb209499381a43302"
SERVICE_REGION = "eastus"

NAME = "Simple transcription"
DESCRIPTION = "Simple transcription description"

LOCALE = "en-US"
#RECORDINGS_BLOB_URI = "https://osaeedstorage.blob.core.windows.net/voicefiles/voiceSample1.wav"

# Set subscription information when doing transcription with custom models
ADAPTED_ACOUSTIC_ID = None  # guid of a custom acoustic model
ADAPTED_LANGUAGE_ID = None  # guid of a custom language model



def transcribe(callid, fileurl):
    logging.info("Starting transcription client...")

    # configure API key authorization: subscription_key
    configuration = cris_client.Configuration()
    configuration.api_key['Ocp-Apim-Subscription-Key'] = SUBSCRIPTION_KEY
    configuration.host = "https://{}.cris.ai".format(SERVICE_REGION)

    # create the client object and authenticate
    client = cris_client.ApiClient(configuration)

    # create an instance of the transcription api class
    transcription_api = cris_client.CustomSpeechTranscriptionsApi(api_client=client)

    # Use base models for transcription. Comment this block if you are using a custom model.
    # Note: you can specify additional transcription properties by passing a
    # dictionary in the properties parameter. See
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/batch-transcription
    # for supported parameters.
    transcription_definition = cris_client.TranscriptionDefinition(
        name=NAME, description=DESCRIPTION, locale=LOCALE, recordings_url=fileurl
    )

    # Uncomment this block to use custom models for transcription.
    # Model information (ADAPTED_ACOUSTIC_ID and ADAPTED_LANGUAGE_ID) must be set above.
    # if ADAPTED_ACOUSTIC_ID is None or ADAPTED_LANGUAGE_ID is None:
    #     logging.info("Custom model ids must be set to when using custom models")
    # transcription_definition = cris_client.TranscriptionDefinition(
    #     name=NAME, description=DESCRIPTION, locale=LOCALE, recordings_url=RECORDINGS_BLOB_URI,
    #     models=[cris_client.ModelIdentity(ADAPTED_ACOUSTIC_ID), cris_client.ModelIdentity(ADAPTED_LANGUAGE_ID)]
    # )

    data, status, headers = transcription_api.create_transcription_with_http_info(transcription_definition)

    # extract transcription location from the headers
    transcription_location: str = headers["location"]

    # get the transcription Id from the location URI
    created_transcription: str = transcription_location.split('/')[-1]

    logging.info("Created new transcription with id {}".format(created_transcription))

    logging.info("Checking status.")

    completed = False

    while not completed:
        running, not_started = 0, 0

        # get all transcriptions for the user
        transcriptions: List[cris_client.Transcription] = transcription_api.get_transcriptions()

        # for each transcription in the list we check the status
        for transcription in transcriptions:
            if transcription.status in ("Failed", "Succeeded"):
                # we check to see if it was the transcription we created from this client
                if created_transcription != transcription.id:
                    continue

                completed = True

                if transcription.status == "Succeeded":
                    results_uri = transcription.results_urls["channel_0"]
                    results = requests.get(results_uri)
                    logging.info("Transcription succeeded. Results: ")
                    #logging.info(results.content.decode("utf-8"))
                    transcriptionResult = json.loads(results.content.decode("utf-8"))["AudioFileResults"][0]["CombinedResults"][0]["Display"]
                    print(transcriptionResult)
                    transcriptionResult = transcriptionResult.replace("'", "") #get rid of any single quotes
                    updateStatement = "update {2}.call_center_voice_source set process_status = 'completed' , transcript = '{1}' where call_id = {0};".format(callid, transcriptionResult, ASTRA_KEYSPACE)
                    session.execute(updateStatement)
                else:
                    logging.info("Transcription failed :{}.".format(transcription.status_message))
                    break
            elif transcription.status == "Running":
                running += 1
            elif transcription.status == "NotStarted":
                not_started += 1

        logging.info("Transcriptions status: "
                "completed (this transcription): {}, {} running, {} not started yet".format(
                    completed, running, not_started))

        # wait for 5 seconds
        time.sleep(5)


if __name__ == "__main__":
	# Right now does one check of ready rows.  need to make this an infinite loop that grabs first one and then sleeps for 5 secs

	select_statement = "select * from {0}.call_center_voice_source where process_status = 'ready' limit 5;".format(ASTRA_KEYSPACE)
	rows = session.execute(select_statement)
	for row in rows:
		print (row.call_id, row.call_audio_filetype, row.call_link, row.process_status, row.transcript, row.last_updated)
		RECORDINGS_BLOB_URI = row.call_link
		transcribe(row.call_id, row.call_link)
