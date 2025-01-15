


https://www.youtube.com/watch?v=0UG2x2iWerk

https://www.youtube.com/watch?v=bi0cKgmRuiA 

There are 3 components to create containerized images - 

1) docker file - blue print to create docker images
2) docker images - these docker images are stored in containers & when we build these images, containers are created storing them.
3)  we run these images, our container start running or application is running within which the python scripts start runs & we get results

   Contanerized application -it contains all the dependencies like python libraries , python distribution or base image coming from docker hub, python script etc.

Need to activate/enable virtualization before running docker images
Activate wsl if we are running docker on windows system

   # import base image to get python distribution available. So we import base image from docker hub
   FROM python:3.8

   #



   # image creation
   docker build -t python-imdb
   docker  build --help

### Docker commands 
##### building docker images
 1)docker build -t myapp:latest .
   Builds an image from the Dockerfile in the current directory (.).
   Tags the image as myapp:latest.

2) docker build -t myapp:latest -f MyDockerfile .
   Uses MyDockerfile instead of the default Dockerfile.
3) docker build -t myapp:latest --build-arg MY_VAR=value .
   Passes a build-time variable MY_VAR to the Dockerfile.

4) Pass Build Arguments
   docker build -t myapp:latest --build-arg MY_VAR=value .
   Passes a build-time variable MY_VAR to the Dockerfile.


To list images

--------------

podman images
 
Pod/Container Creation (From VSCode at PWD)

----------------------

pip install podman-compose==1.0.6

podman-compose up
 
Container details (VSCode / Powershell)

-----------------

podman ps -a
 
To restart the container incase stopped/exited (VSCode / Powershell)

------------------------

podman start <container id>
 
 
To work with fastapi application (Browser / Postman)

--------------------------------

http://127.0.0.1:8000
http://localhost:8000
 
Swagger UI (Browser)
-------------
http://127.0.0.1:8000/docs
http://localhost:8000/docs
The source for the Linux kernel used in Windows Subsystem for Linux 2 (WSL2) - microsoft/WSL2-Linux-Kernel
 


  


