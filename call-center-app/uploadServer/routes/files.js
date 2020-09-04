let express = require('express');
let router = express.Router();

let fileService = require('../lib/gcp_store');
let userService = require('../lib/users');

let uploadsDir = process.env.UPLOAD_DIR + '/';
let googleStorageBucketName = process.env.GOOGLE_STORAGE_BUCKET_NAME;

function uploadFile(req, res, file2Upload) {
    return fileService.uploadFile(file2Upload, googleStorageBucketName)
        .then((retData) => {
            return;
        }).catch((errData=>{
            console.error('Could not upload file ' + file2Upload + '|bucket=' + googleStorageBucketName);
            console.error(errData);
            throw new Error('Could not store file');
    }));
}

function acceptFileFromUser(req, res) {
    try {
        if(!req.files) {
            res.status(400).send({
                status: false,
                message: 'No file uploaded'
            });
        } else {
            //Use the name of the input field (i.e. "file2Upload") to retrieve the uploaded file
            let file2Upload = req.files.audio_message;

            //Use the mv() method to place the file in upload directory (i.e. "uploads")
            file2Upload.mv(uploadsDir + file2Upload.name)
                .then((retData) => {
                    uploadFile(req, res, uploadsDir + file2Upload.name)
                        .then(retData => {
                            // YUCK!!  Hard coded strings used in multiple places :-(  YUCK, YUCK!!
                            //            gs://astra_call_center/1599237336336-demo1.wav
                            let fileNameOnStore = 'gs://' + googleStorageBucketName + '/' + file2Upload.name;
                            userService.recordAudioFileLocation(fileNameOnStore)
                                .then((retData) => {
                                    return res.status(200).send({
                                        status: true,
                                        code: 0,
                                        message: "Success",
                                        id: retData.id
                                    });

                                }).catch((errData) => {
                                console.error('Failed to register the speech with the user');
                                return res.status(503).send({
                                    status: false,
                                    code: 18,
                                    message: "Could not register the audio file in Astra"
                                });
                            })

                        }).catch(errData => {
                        console.error(errData);
                        return res.status(500).send({
                            status: false,
                            code: 19,
                            message: "Could not upload file into Cloud provider's store"
                        });
                    });
                });
        }
    } catch (err) {
        res.status(500).send(err);
    }
}

/* GET users listing. */
router.post('/', function(req, res, next) {

    (userService.authenticateToken(req,res, acceptFileFromUser));



});

module.exports = router;
