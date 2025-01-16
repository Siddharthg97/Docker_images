ARG basePythonOSVersion=3.10
FROM docker.artifacts.walmart.com/wce-docker/ca-roots:latest as roots
FROM docker.ci.artifacts.walmart.com/hub-docker-release-remote/library/python:${basePythonOSVersion}
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

RUN rm -rf /etc/apt/sources.list \
  && rm -rf /etc/apt/sources.list.d/*

RUN echo "deb [trusted=yes] http://ark-repos.wal-mart.com/ark/apt/published/debian/11.0/direct/soe/noenv/os/ bullseye main" >> /etc/apt/sources.list
RUN echo "deb [trusted=yes] http://ark-repos.wal-mart.com/ark/apt/published/debian/11.0/direct/soe/noenv/updates/ bullseye-updates main" >> /etc/apt/sources.list
RUN echo "deb [trusted=yes] http://ark-repos.wal-mart.com/ark/apt/published/debian/11.0/direct/soe/noenv/security/ bullseye-security main" >> /etc/apt/sources.list
RUN echo "deb [trusted=yes] http://ark-repos.wal-mart.com/ark/apt/published/debian/11.0/direct/soe/noenv/third-party/ bullseye main" >> /etc/apt/sources.list
RUN echo "deb [trusted=yes] http://ark-repos.wal-mart.com/ark/apt/published/debian/11.0/direct/soe/noenv/wm-apps/ bullseye main" >> /etc/apt/sources.list

RUN apt-get update \
    && apt-get install gcc -y \
    && apt install python3-pip -y \
    && apt install unixodbc-dev -y \
    && apt-get clean

RUN apt-get install --yes --no-install-recommends \
        apt-transport-https \
        curl \
        gnupg \
        unixodbc-dev\
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/ubuntu/19.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install --yes --no-install-recommends msodbcsql17 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /tmp/*

COPY --from=roots /usr/local/share/ca-certificates /usr/local/share/ca-certificates
COPY --from=roots /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
RUN rm -f /etc/ssl/cert.pem && ln -s /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem

RUN python3 -m pip install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip   
RUN pip install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org "dask[complete]==2024.6.2"
RUN pip install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/samsdse-pypi/simple samsclub-samsdse-wmfs
RUN pip3 install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org google-cloud-secret-manager==2.16.1
RUN pip install --proxy=http://sysproxy.wal-mart.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org protobuf==3.20.3

COPY ./src /code/src
RUN adduser -u 10000 goc
USER 10000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]





