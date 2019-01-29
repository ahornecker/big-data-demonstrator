from ubuntu:latest
RUN apt-get update; apt-get install -y python3.5

# create user and copy files
RUN groupadd feinstaub && useradd -m -g feinstaub feinstaub

ADD files /home/feinstaub/

ENTRYPOINT sleep infinity