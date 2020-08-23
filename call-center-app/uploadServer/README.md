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

