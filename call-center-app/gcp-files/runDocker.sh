docker build -t call_center_transcriber:1.0 . \
&& docker run \
--env GOOGLE_APPLICATION_CREDENTIALS=./fieldops-gce-presales-a5ec0edbb261.json  \
--name call_center_transcriber \
call_center_transcriber:1.0