# flaskToCloudRun
This code documents the following steps
- Building a Dockerfile, so that you can containerize a Python workflow
- For Cloud Run, we need a web server which listens on port 80, so we are using a Flask app
- In the Flask App, we are calling a shell script
- Finally, we use the [Google Cloud article](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) to push this to Cloud Run

Let's understand why we even need this in the first place, and alternative workflows. You can decide the best course of action for your use case depending on some of these considerations.
## Main Objective
- We have a [scrapy](https://docs.scrapy.org/en/latest/intro/overview.html) repository that fetches data from certain pages, and we want to be able to schedule it
### Considerations
It can be tricky to simply schedule something on Google Cloud. If you have your own local machine, you can use a cron job on Unix or you could use Task Scheduler on Windows. (Actually, both of them are not as simple as they sound - cron job is sometimes tricky because of different user profiles, PATH variables etc and Task Scheduler is not the most intuitive as well, but generally experienced users are familiar enough to tackle this locally so we would not delve too deep into that). If you are using a Cloud Provider though, lets look at some of our options
- You do of course have the option to install a machine (isnt that the very core function of a cloud service provider, you might ask?). However, then you have to manually install a bunch of libraries etc, build out connections, make sure services are accessible and what not. You are welcome to try this path, and its a valid approach. Its called Compute Engine on GCP. I have tried it, and it gave me a lot of headache, so I am not choosing this path
- On that note, instead of a cron job directly, there might be some packages or wrappers like [schedule](https://schedule.readthedocs.io/en/stable/). Again this would need a machine to be available to work. Google Cloud for example provides cloud shell but that's ephemeral and only remains in use for your session. Using a Compute Engine instance with this library might be a slightly easier path though
- You can use Cloud Functions to incorporate the function, then use Cloud Scheduler to schedule a cron job. I really like this option for simple tasks. However, for large projects with a lot of interdependent files, libraries etc, it can be tricky to set up, case in point this particular repository. 
- Now, we come to one of the options that will work for pretty much any use case. You can containerize the repository into a Docker image, and then create a Google Kubernetes cluster to schedule it. Sorry for throwing a bunch of jargon there - Docker, Container, Kubernetes - what is going on? This might need some explaining
   - You can find the official explanations for Docker on several sites. [Example](https://www.ibm.com/sg-en/topics/docker). Before I used it myself though, I was never quite able to make sense of this language and internalize what this meant. This is how I understand it now. If you want to implement a script like this, you shall obviously need a bunch of libraries, a specific type of environment etc. That is why Compute Engine was so tough, isnt it, because you have to spend a bunch of time installing and configuring things. To oversimplify, what if you could provide a configuration file such that the system could just set up the environment by itself and give you the output on a single click? That is what Docker enables you to do. You have a container which contains language that the system understands to know what stuff to install, execute etc
   - That configuration file is called Dockerfile. Its actually fairly simple to build one. Take a look at the [official documentation](https://docs.docker.com/language/python/build-images/) to understand how to build one, which enables you to build the container image, and then you can run it. If its easy to understand for you, then in a way you could consider it analogous to setting up a virtual environment when you run it
   - On Google Cloud, if you are doing this, you can follow [this documentation](https://cloud.google.com/build/docs/building/build-containers#use-dockerfile). Below are the specific commands I used for this to work (running from the directory with the Dockerfile)
   ```
  	 gcloud artifacts repositories create scrapy-docker-repo --repository-format=docker --description="Docker repository" --location=us-west2 

	 gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/engaged-carving-363913/scrapy-docker-repo/scrapy-image:tag1

	gcloud auth configure-docker us-west2-docker.pkg.dev
   #(needed to use this as there was some error I had gotten while directly trying to run)

	docker run us-west2-docker.pkg.dev/engaged-carving-363913/scrapy-docker-repo/scrapy-image:tag1
  ```
  
  - Once this is done, you should see the repository in "Artifact Registry" on Google Cloud. You can do the gcloud build submit again, and it will update the image, basically push a new image, but mark it as the latest, by putting the tag, so essentially replace it, but still preserve the old copy
  - The next step is to build out the Kubernetes cluster. Kubernetes technically is a container orchestration platform, but simply put, its the system that allows you to manage running these containers efficiently. You can create using [this documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster) and specify the image from the registry
  - Post that, you can set up a [cron job](https://cloud.google.com/kubernetes-engine/docs/how-to/cronjobs#creating). Here is an example of the yaml file called cronjob.yaml and you can apply it by just doing a kubectl apply -f cronjob.yaml. Its useful to understand kubectl commands [here](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
   ```
   
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: uac-image-sha256-1
   spec:
     schedule: "*/10 * * * *"
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: uac-image-sha256-1
               image: us-west2-docker.pkg.dev/idz-gg-ads/uac-repo/uac-image@sha256:b71b39ce8acdfd09d8f2be96dd33dd3f43196ac625ae3284a3e8f9a8554ad6bd
               imagePullPolicy: IfNotPresent            
             restartPolicy: OnFailure
    ```
- Finally, lets come to what I actually recommend doing. The Kubernetes cluster approach will definitely work, but the option to use Cloud Run is a bit easier to me. For this method, you need a Dockerfile as well, and then all you need to do is gcloud run deploy from the command shell. [This article](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) guides you through the process. Cloud Run has a 60 mins max timeout, compared to Cloud Functions, which only has 9 mins
