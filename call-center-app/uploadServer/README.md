# Demo narrative

This micro-service supports a Call Center use case where customers call in and leave a message so that a CSR can process
and then call them back.

The idea is that the customer's dialog allows the enterprise to direct the call to the CSR, for e.g.:

1. Hey, I have a problem with my internet!  It is down right now!!!
1. I want to upgrade my internet service


# This service

This micro-service 

1. Exposes an API to autheticate the customer.  The customer's user ID and password are stored in an Astra table.
1. Exposes an API to accept a speech i.e. WAV files
1. Uploads the WAV file to GCP Storage (TBD: S3, Azure)
1.1. Updates an Astra table that maps a user with their message
1. Exposes an API to query the Astra table to see if the speech was transcribed 
(using cloud provider's transcription service)


## Usage

You need to ensure you can connect to Astra correctly:

- ENV vars to set credentails 
