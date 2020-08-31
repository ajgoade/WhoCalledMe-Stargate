const {Client} = require('cassandra-driver');
let jwt = require('jsonwebtoken');
let client;
let astraUser = process.env.ASTRA_USER;
let astraUserPwd = process.env.ASTRA_USER_PWD;
let astraSecureBundleFilePath = process.env.ASTRA_SECURE_BUNDLE_FILE_PATH;
let initFailure = false;

///////////////////////////////////////////////////////////////////////
// Helper to open connection to Astra
///////////////////////////////////////////////////////////////////////
function openAstra(astraCredentialsZipFile, username, pwd) {
    client = new Client({
        cloud: {secureConnectBundle: astraCredentialsZipFile},
        credentials: {username: username, password: pwd}
    });
    return client.connect();
}

function invalidUserPayload() {
    return ( {
        errCode: 1
    });
}

console.debug('astraCreds|' + astraUser + '|' + astraUserPwd + '|' + astraSecureBundleFilePath);
openAstra(astraSecureBundleFilePath, astraUser, astraUserPwd)
    .then((retData) => {
        console.debug(retData);
    }).catch((retData) => {
    console.error(retData);
    initFailure = true;
});


function generateAccessToken(username) {
    let token =  jwt.sign({sub_id: username}, process.env.TOKEN_SECRET, { expiresIn: '900s' });
    return token;
}

function validUserJwt(username) {
    return({
        errCode:0,
        jwt: generateAccessToken(username)
    })
}



let users;
users = {
    loginSucceeded: function (username, pwd) {
        // console.debug('look for|user=' + username + '|pwd=' + pwd);

        let cql = 'SELECT * FROM call_center_app.users where ' +
            "username='" + username + "' " +
        " AND " +
        "password='" + pwd + "' ";

        console.log(cql);

        return client.execute(cql)
            .then((retData) => {
                // console.debug(retData);
                let userRec = retData.rows;
                if (userRec.length === 0) {
                    return invalidUserPayload();
                }

                return validUserJwt(username);
            }).catch((retData) => {
                console.debug(retData);
                return invalidUserPayload();
            });
    },

    authenticateToken: function (req, res, next) {
        // Gather the jwt access token from the request header
        const authHeader = req.headers['authorization'];
        const token = authHeader && authHeader.split(' ')[1];
        if (token == null) return res.sendStatus(401); // if there isn't any token

        jwt.verify(token, process.env.TOKEN_SECRET, (err, user) => {
            console.log(err);
            if (err) return res.sendStatus(403);
            req.user = user;
            next(req, res) // pass the execution off to whatever request the client intended
        });
    }, // authenticateToken


}; //users

module.exports = users;