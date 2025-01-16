We need following files to create walmart application
1)Dockerfile
2)app folder - This contains many python edior file to be used module in main.py
2)config.py - contains all the functions/wrappers to accesss the resources like azure data bricks, gcp connections
3)compose.yml -  that contains all the environment varibles like proxy address, ports, 
4)featurestore_dev.json - that contains all the credentials to access the feature store


Steps to  build docker image
1) create app folder having all editor scripts and main.py
2) create config file, compose.yml, json file store private keys
3) create docker file
