# astra_demos
temporary repo for storing and collaborating on all Astra Demos for the technical field team

**Create a NEW folder for every new use case and sub-folders for tasks/components in each use case**

## Call Center App

We want to simulate a customer interacting with an IVR system and
that speech is captured as a WAV file.  The file is placed on S3, 
Astra is used to track it, a AWS transcription service is used to 
convert it to text, and Astra is updated with the text.

Yes, an EC2, AWS Lambda, or K8s docker container resource will be
needed as the middleware to track the above.

 