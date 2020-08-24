/**
 * Sample program from https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
 */
const bucketName = 'call-center-inbound';
const filename = './sample__audio_files/YouKnowNothingJonSnow.m4a';

// Imports the Google Cloud client library
const {Storage} = require('@google-cloud/storage');

// Creates a client
const storage = new Storage();

async function uploadFile() {
    // Uploads a local file to the bucket
    await storage.bucket(bucketName).upload(filename, {
        // Support for HTTP requests made with `Accept-Encoding: gzip`
        gzip: true,
        // By setting the option `destination`, you can change the name of the
        // object you are uploading to a bucket.
        metadata: {
            // Enable long-lived HTTP caching headers
            // Use only if the contents of the file will never change
            // (If the contents will change, use cacheControl: 'no-cache')
            cacheControl: 'public, max-age=31536000',
        },
    });

    console.log(`${filename} uploaded to ${bucketName}.`);
}


let gcp_storage_service;
gcp_storage_service = {
    uploadFile: function (filePath, bucketName) {
        return uploadFile()
            .then((retData) => {
                return true;
            })
            .catch((retData) => {
                console.error(retData);
                return false;
            });

    },


}; //users

module.exports = gcp_storage_service;