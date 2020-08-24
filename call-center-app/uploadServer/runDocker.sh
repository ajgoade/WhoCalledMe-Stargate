
source ./config/astraCreds.sh

docker container rm call_center_uploader

docker run \
--env GOOGLE_APPLICATION_CREDENTIALS="./gcpConfig/rajeev-personal-cc-storage-admin-d3ded273b239.json" \
--env ASTRA_USER='rajeev' \
--env ASTRA_USER_PWD='astraRocks1' \
--env ASTRA_SECURE_BUNDLE_FILE_PATH='./astraConfig/rajeev-secure-connect-graphdbname.zip' \
--env TOKEN_SECRET="09f26e402586e2faa8da4c98a35f1b20d6b033c6097befa8be3486a829587fe2f90a832bd3ff9d42710a4da095a2ce285b009f0c3730cd9b8e1af3eb84df6611" \
--env PORT=3030 \
-v uploads:uploads \
-p 3030:3030 \
--name call_center_uploader \
-t call_center_uploader:1.0




