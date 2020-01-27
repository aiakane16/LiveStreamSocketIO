FROM gitpod/workspace-mysql

USER root

RUN pyenv install 3.6.10 
RUN pyenv global 2.7.17 3.6.10

RUN git clone https://github.com/thtrieu/darkflow ./webserver/darkflow

RUN pip3 install django djangorestframework django-cors-headers Cython Pillow opencv-python scikit-image scikit-learn tensorflow==1.8.0

RUN pip3 install ./webserver/darkflow




