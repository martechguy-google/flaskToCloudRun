# flaskToCloudRun
This code documents the following steps
- Building a Dockerfile, so that you can containerize a Python workflow
- For Cloud Run, we need a web server which listens on port 80, so we are using a Flask app
- In the Flask App, we are calling a shell script
- Finally, we use the [Google Cloud article](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) to push this to Cloud Run
