FROM gitpod/workspace-mysql

USER root

RUN add-apt-repository -r ppa:jonathonf/python-3.6 -Y

RUN apt-get update 

RUN apt-get upgrade

RUN apt-get install python3.6

