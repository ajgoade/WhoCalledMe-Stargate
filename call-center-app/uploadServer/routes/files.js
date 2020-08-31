let express = require('express');
let router = express.Router();

let fileService = require('../lib/gcp_store');
let userService = require('../lib/users');

let uploadsDir = process.env.UPLOAD_DIR + '/';

function uploadFile(req, res, file2Upload) {
    fileService.uploadFile(file2Upload, "astra_call_center")
        .then((retData) => {
            res.status(200).send("File uploaded");
        }).catch((errData=>{
        res.status(500).send(errData);
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
                    uploadFile(req, res, uploadsDir + file2Upload.name);
                }).catch((errData) => {
                    console.error(errData);
                    res.status(500).send(errData);
            })

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
