# Extreme prototype for authenticated file upload  

OK, we will check the user name and password against
call_center_app.users.  This will simulate a customer
calling into the Call Center, or a customer service
agent.

# This service


Ensure user is logged in, and allow them to upload a
WAV file.

Should be two separate services, the login service should
return a JWT and the uploader should validate JWT.  We 
don't do that right now.

## Usage


# GCP Cloud Storage hints

I used https://cloud.google.com/storage/docs/reference/libraries?hl=en_US#client-libraries-install-nodejs

I created a project
I created a cloud storage services account - call-center-app-*.json

1. Source - I used the file under the PostmanAPI dir to get a token and upload a file .
2. Dest - Uploads to Rajeev's personal GCP console system
3. Astra - TBD TBD TBD TODO TODO
 