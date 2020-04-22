# Pull base image.
FROM centos:7.2.1511

# Build commands
ENV PYTHONUNBUFFERED 1
RUN yum -y update; yum clean all
RUN yum install -y python3-setuptools gcc gcc-c++ python3-devel.x86_64 ImageMagick-devel; yum clean all
RUN echo -e "[mongodb-org-3.0] \n\
name=MongoDB Repository \n\
baseurl=http://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/3.0/x86_64/ \n\
gpgcheck=0 \n\
enabled=1" >> /etc/yum.repos.d/mongodb-org-3.0.repo
RUN yum install -y mongodb-org; yum clean all

RUN python3 -V

# virtualenv activation
RUN easy_install-3.6 pip
RUN mkdir /opt/social-network
WORKDIR /opt/social-network
ADD requirements.txt /opt/social-network/
RUN pip install -r requirements.txt
ADD . /opt/social-network

# Fix UTF-8
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# start the app server
ENV FLASK_APP manage.py
CMD flask run
