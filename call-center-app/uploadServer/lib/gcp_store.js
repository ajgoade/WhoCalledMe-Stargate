/**
 * Sample program from https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
 */
const bucketName = 'astra_call_center';
const filename = './sample__audio_files/YouKnowNothingJonSnow.m4a';

// Imports the Google Cloud client library
const {Storage} = require('@google-cloud/storage');

// Creates a client
const storage = new Storage();

function uploadFile(filename, bucketName) {
    // Uploads a local file to the bucket
    return storage.bucket(bucketName).upload(filename, {
        // Support for HTTP requests made with `Accept-Encoding: gzip`
        // gzip: true, --20200831 - ajgoade - Removed - Causing files to be unreadable
        // By setting the option `destination`, you can change the name of the
        // object you are uploading to a bucket.
        metadata: {
            // Enable long-lived HTTP caching headers
            // Use only if the contents of the file will never change
            // (If the contents will change, use cacheControl: 'no-cache')
            cacheControl: 'public, max-age=31536000',
        },
    });

}


let gcp_storage_service;
gcp_storage_service = {
    uploadFile: function (filePath, bucketName) {
        return uploadFile(filePath, bucketName)
            .then((retData)=> {
                // console.log(retData);
                console.log(`${filePath} uploaded to ${bucketName}.`);
                return true;
            }).catch((errData)=> {
                console.error(`${filePath} FAILED to upload to ${bucketName}.`);
                console.error(false);
                return false;
            })

    },


}; //users

module.exports = gcp_storage_service;
