let express = require('express');
let userService = require('../lib/users');
let router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});

router.post('/', function(req,res, next) {
  let userID = req.body.userID;
  let pwd = req.body.pwd;

  console.log('request body is===>');
  console.log(req.body.userID);
  console.log(req.body.pwd);

  userService.loginSucceeded(userID, pwd)
      .then((retData) => {
        res.send('Login succeeded');

      }).catch((retData) => {

        res.status(401).send('Login failed');
      });

});

module.exports = router;
