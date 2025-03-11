https://www.youtube.com/watch?v=0UG2x2iWerk
https://www.youtube.com/watch?v=bi0cKgmRuiA 

There are 3 stages to create containerized images - 

1) docker file - blue print to create docker images
2) docker images - we build these images, containers are created storing them. these are set of instructions on how a container is suppose to run.
3) containers -  when these docker images are made to run containers are created. These containers cn be stopeed, started as per requirement. these containers it contains all the dependencies like python libraries , python distribution or base image coming from docker hub, python script etc.

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





No, containers do not "contain" the Docker image itself. Instead, they are instantiated from the image. Here’s how it works:

Relationship Between Docker Images and Containers
Docker Image:

A blueprint or template for the container.
Immutable and contains everything needed to run an application (e.g., code, libraries, dependencies, etc.).
Read-only and can be reused to create multiple containers.
Docker Container:

A runtime instance of a Docker image.
When a container is created from an image, the image is used as the base, and a writable layer is added on top of it.
The writable layer allows the container to modify files, save data, or make other changes during its lifecycle without altering the original image.
Lifecycle of a Container
Image -> Container:

When you create a container, Docker takes the specified image and launches it as a container.
Example:

docker run ubuntu
Docker takes the ubuntu image and creates a container from it.
Changes in the Container:

Any modifications made inside the container (e.g., installing software or modifying files) are stored in the writable layer specific to that container.
These changes do not affect the original image.

Container Independence:
Each container runs independently, even if created from the same image.
Multiple containers can be created from a single image, each with its own writable layer and isolated environment.









Creating a container using Docker involves pulling a prebuilt image or using your own built image and running it with the docker run command. Here's a step-by-step guide:

Steps to Create a Container
Ensure Docker is Installed

Check if Docker is installed and running on your system:docker --version
Install Docker from Docker's official site if not installed.
Pull or Build an Image

Pull an image from Docker Hub:docker pull <image-name>
Example:docker pull ubuntu
Build your own image from a Dockerfile:docker build -t <image-name> .
Example: docker build -t my-app .
Run a Container Use the docker run command to create and start a container:docker run [OPTIONS] <image-name>

Common Options for docker run
Interactive Mode: To run the container interactively:docker run -it <image-name> /bin/bash
Detached Mode: To run the container in the background:docker run -d <image-name>
Name Your Container: Assign a name to the container:docker run --name <container-name> <image-name>
Port Mapping: Map container ports to your host:docker run -p <host-port>:<container-port> <image-name>


















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
 


  


