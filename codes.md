

https://www.youtube.com/watch?v=0UG2x2iWerk

https://www.youtube.com/watch?v=bi0cKgmRuiA 


**Following are the codes to create docker images , containerize them & generate end point urls
Enable the Windows Subsystem for Linux (From Powershell Admin)

-------------------------------------------------------------

dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
 
Enable Virtual Machine feature (Also Raise ticket to enable virtualization) (From Powershell Admin)

---------------------------------------------------------------------------------------------------

dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
 
Download the Linux kernel update package

----------------------------------------

https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
 
Set WSL 2 as your default version (From Powershell Admin)

---------------------------------------------------------

wsl --set-default-version 2
wsl -v
 
Podman Desktop Download (download/install podman server v5.2.5 while doing setup)

-----------------------------------------------------------------------------------
https://github.com/podman-desktop/podman-desktop/releases/download/v1.14.1/podman-desktop-1.14.1-setup-x64.exe
 
Set Proxy (From Powershell Admin)

---------------------------------

$env:HTTP_PROXY = "http://sysproxy.wal-mart.com:8080"

$env:HTTPS_PROXY = "http://sysproxy.wal-mart.com:8080"
 
Podman Machine Setup (From Powershell Admin)

--------------------------------------------

podman machine list

podman machine init

podman machine start
wsl -l -v
 
Image Creation (From VSCode at PWD)

---------------

podman --log-level=debug build -t sams-md-api .
 
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
 
