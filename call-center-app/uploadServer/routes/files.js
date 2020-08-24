let express = require('express');
let router = express.Router();

let fileService = require('../lib/gcp_store');
let userService = require('../lib/users');

function uploadFile(req, res) {
    fileService.uploadFile("../package.json", "call-center-app")
        .then((retData) => {
            res.status(200).send("File uploaded");
        }).catch((errData=>{
        res.status(500).send(errData);
    }));
}

/* GET users listing. */
router.post('/', function(req, res, next) {

    (userService.authenticateToken(req,res, uploadFile));

});

module.exports = router;
