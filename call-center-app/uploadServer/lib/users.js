const {Client} = require('cassandra-driver');
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
        cloud: { secureConnectBundle: astraCredentialsZipFile },
        credentials: { username: username, password: pwd }
    });
    return client.connect();
}

console.debug('astraCreds|' + astraUser + '|' + astraUserPwd + '|' + astraSecureBundleFilePath);
openAstra(astraSecureBundleFilePath, astraUser, astraUserPwd)
    .then((retData) => {
        console.debug(retData);
    }).catch((retData) => {
    console.error(retData);
    initFailure = true;
});


let users;
users = {
    loginSucceeded: function (username, pwd) {
        // console.debug('look for|user=' + username + '|pwd=' + pwd);

        let cql = 'SELECT * FROM call_center_app.users where ' +
            "username='" + username + "' ";

        console.log(cql);

        return client.execute(cql)
            .then((retData) => {
                // console.debug(retData);
                return true;
            }).catch((retData) => {
            console.debug(retData);
            return false;
        });
    }
}; //users

module.exports = users;