
docker container rm upload_client
#
#
#
docker run -p 4201:80 --name upload_client  -t upload_client:1.0

echo "Please connect to this docker instance on port 4201 for e.g. http://localhost:4201/login"
