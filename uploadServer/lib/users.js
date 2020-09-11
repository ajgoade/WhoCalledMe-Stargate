const {Client} = require('cassandra-driver');
const TimeUuid = require('cassandra-driver').types.TimeUuid;
let moment = require('moment');
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
    let token =  jwt.sign({sub_id: username}, process.env.TOKEN_SECRET, { expiresIn: '1800s' });
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

        let cql = 'SELECT * FROM callcenter.users where ' +
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


    recordAudioFileLocation: function(audioFilePath) {

        console.log('Astra registration for new file = ' + audioFilePath);
        const id = TimeUuid.now();

        let cql = 'INSERT into callcenter.call_center_voice_source ' +
            '(call_id, call_audio_filetype, call_link, process_status, last_updated) ' +
            'values (' +
            id +
            ', ' +
            '\'wav\', ' +
            '\'' + audioFilePath + '\', ' +
            '\'new\', ' +
            moment.now() +
            ')'
        ;

        console.log(cql);

        return client.execute(cql)
            .then((retData) => {
                console.debug(retData);
                return ({
                    id:id,
                    success: true
                });

            }).catch((retData) => {
                console.debug(retData);
                throw new Error('could not upload file; err is ' + JSON.stringify(retData));
            });
    }, // ()


    /*
     * Use the ID to ask the server for the transcription...a transcription could take up to 3 minutes!
     */
    getAudioFileTranscription: function(req, res, next) {

        let id = req.params.id;

        let cql = 'SELECT * FROM  callcenter.call_center_voice_source ' +
            ' WHERE call_id=' +
            id;

        console.log(cql);

        return client.execute(cql)
            .then((retData) => {
                // console.debug(retData);
                return res.status(200).send({
                    id:id,
                    data: retData.rows
                });

            }).catch((retData) => {
                console.error(retData);
                return res.status(403).send({
                    code:20,
                    message: 'Could not get transcription for audio file with id=' + id,
                    errDetails: JSON.stringify(retData)
                })
            });
    } // getAudioFileTranscription



}; //users

module.exports = users;
