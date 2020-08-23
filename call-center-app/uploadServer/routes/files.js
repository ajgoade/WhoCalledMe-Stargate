let express = require('express');
let router = express.Router();

let fileService = require('../lib/gcp_store');


/* GET users listing. */
router.post('/', function(req, res, next) {

    fileService.uploadFile("../package.json", "call-center-app");

});

module.exports = router;
