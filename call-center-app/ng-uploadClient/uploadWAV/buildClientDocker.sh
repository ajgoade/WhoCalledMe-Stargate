
#
#  First build the html files via Angular
#

npm run build --prod


#
#  Build a docker image with the name upload_client.  This is the UI of the Call Center App
# that allows a user to record an audio file and upload to the service using APIs
#
docker build  -t upload_client:1.0 -f Dockerfile .

