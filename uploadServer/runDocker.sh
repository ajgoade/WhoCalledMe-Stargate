
source ./config/astraCreds.sh

export CONTAINER_UPLOAD_DIR='/uploads'
export HOST_UPLOAD_DIR=$(pwd)/uploads

docker stop call_center_uploader_server
docker container rm call_center_uploader_server

docker run \
--env GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
--env ASTRA_USER=$ASTRA_USER \
--env ASTRA_USER_PWD=$ASTRA_USER_PWD \
--env ASTRA_SECURE_BUNDLE_FILE_PATH=$ASTRA_SECURE_BUNDLE_FILE_PATH \
--env TOKEN_SECRET=$TOKEN_SECRET \
--env PORT=$PORT \
--env UPLOAD_DIR=$CONTAINER_UPLOAD_DIR \
--env GOOGLE_STORAGE_BUCKET_NAME=$GOOGLE_STORAGE_BUCKET_NAME \
-v $HOST_UPLOAD_DIR:$CONTAINER_UPLOAD_DIR \
-p 3030:3030 \
--name call_center_uploader_server \
-t call_center_uploader_server:1.0
