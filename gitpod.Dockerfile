FROM gitpod/workspace-mysql

USER root

RUN pyent install 3.6.10 
RUN pyenv global 2.7.17 3.6.10




