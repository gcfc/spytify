const fetch = require('node-fetch')

async function scanActivity(accessToken) {
    const response = await
        fetch('https://guc-spclient.spotify.com/presence-view/v1/buddylist', {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        })
    return response.json()
}

async function main(accessToken) {
    const activity = await scanActivity(accessToken)
    console.log(JSON.stringify(activity, null, 2))
}

// Check if at least one argument (other than node and script path) is provided
if (process.argv.length < 3) {
    console.error('Please provide a string argument.');
    process.exit(1);
}

// Extract the string argument from command line
const accessToken = process.argv[2];
main(accessToken)