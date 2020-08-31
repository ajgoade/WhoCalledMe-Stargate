let express = require('express');
let userService = require('../lib/users');
let router = express.Router();


function validUser(req, res) {
    res.status(200).send("Valid user");
}
/* GET users listing. */
router.get('/', function(req, res, next) {

    userService.authenticateToken(req, res, validUser);

});

router.post('/', function(req,res, next) {
  let userID = req.body.userID;
  let pwd = req.body.pwd;

  console.log('request body is===>');
  console.log(req.body.userID);
  console.log(req.body.pwd);

  userService.loginSucceeded(userID, pwd)
      .then((retData) => {
          if (retData.errCode != 0) {
              res.status(401).send('Login failed');
          }

        res.status(200).send(retData);

      }).catch((retData) => {

        res.status(401).send('Login failed');
      });

});

module.exports = router;
