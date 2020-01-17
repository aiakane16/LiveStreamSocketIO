FROM gitpod/workspace-mysql

USER root

RUN add-apt-repository -r -y ppa:jonathonf/python-3.6

RUN apt-get -y update 

RUN apt-get -y upgrade

RUN apt-get install python3.6

