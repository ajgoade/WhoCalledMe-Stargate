let express = require('express');
let router = express.Router();

let fileService = require('../lib/gcp_store');
let userService = require('../lib/users');

function uploadFile(req, res, file2Upload) {
    fileService.uploadFile(file2Upload, "call-center-inbound")
        .then((retData) => {
            res.status(200).send("File uploaded");
        }).catch((errData=>{
        res.status(500).send(errData);
    }));
}

function acceptFileFromUser(req, res) {
    try {
        if(!req.files) {
            res.send({
                status: false,
                message: 'No file uploaded'
            });
        } else {
            //Use the name of the input field (i.e. "file2Upload") to retrieve the uploaded file
            let file2Upload = req.files.audio_message;

            //Use the mv() method to place the file in upload directory (i.e. "uploads")
            file2Upload.mv('./uploads/' + file2Upload.name);

            uploadFile(req, res, './uploads/' + file2Upload.name);
            // //send response
            // res.send({
            //     status: true,
            //     message: 'File is uploaded',
            //     data: {
            //         name: file2Upload.name,
            //         mimetype: file2Upload.mimetype,
            //         size: file2Upload.size
            //     }
            // });

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
