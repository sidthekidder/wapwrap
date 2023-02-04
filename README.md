## Whatsapp Wrapped - visualize your whatsapp conversations
See the summary of your whatsapp history with any contact or group conversation. Simply download the chat log using the Export Chat option, and upload the text file using the app UI. A pdf containing the chat analysis is automatically downloaded for you.

[Instructions for chat export](https://faq.whatsapp.com/1180414079177245/?cms_platform=android)

[How-to video](https://www.youtube.com/watch?v=8BwGj9ssZSY&t=36s)


## Installation
```
# build docker image
# replace the already existing docker image tags in wapwrap-deployment.yaml and docker-compose.yml with the newly generated tags
bentoml containerize wapwrap-sentimentservice:latest
docker build --no-cache -t wapwrap .

# test locally
docker-compose up

# deploy to kubernetes 
kubectl apply -f wapwrap-deployment.yaml
```

## System Architecture

- The whatsapp wrapped service runs as a kubernetes cluster with 2 pods. It can be deployed either via `docker-compose up` or `kubectl apply -f wapwrap-deployment.yaml`.
- The main wapwrap service is a java spring API server which accepts a whatsapp chat log and returns the pdf analysis. It interfaces with the jupyter notebook environment using the `nbconvert` command line tool. It also hosts a basic frontend UI allowing the user to upload chat logs and download the resulting analysis.
- The jupyter notebook is run on the input chat log using `nbconvert` which executes all notebook cells and exports the output as pdf. This notebook also calls the prediction service API which is running the sentiment analysis model.
- The prediction service API runs in a separate pod which can be scaled independently of the java REST API. It uses the bentoML serving framework which can be easily integrated with huggingface's transformer pipelines. The `distilbert-base-uncased-finetuned-sst-2-english` model is used for making inferences about sentiment per line in the whatsapp chat log.

![system design](https://raw.githubusercontent.com/sidthekidder/wapwrap/master/images/sysdesign.png)


## Chat Analysis

- The jupyter notebook uses several visualizations like messages frequency over time and day, wordcloud, topic modelling, emoji and sentiment analysis.
- More techniques can be added easily. Since the notebook output is directly exported as pdf, only a new python cell is required for each new viz.

![analysis-1](https://raw.githubusercontent.com/sidthekidder/wapwrap/master/images/analysis-0.png)

![analysis-2](https://raw.githubusercontent.com/sidthekidder/wapwrap/master/images/analysis-1.png)

![analysis-3](https://raw.githubusercontent.com/sidthekidder/wapwrap/master/images/analysis-2.png)


