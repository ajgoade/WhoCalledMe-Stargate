docker build -t 1.0 . \
&& docker run \
--env GOOGLE_APPLICATION_CREDENTIALS=./fieldops-gce-presales-a5ec0edbb261.json \
--name process-files  \
1.0