FROM jupyterhub/jupyterhub:0.7.2
RUN apt-get update && apt-get install make

COPY . /srv/everware
WORKDIR /srv/everware/
RUN make install

EXPOSE 8000
EXPOSE 8081

ENTRYPOINT ["/srv/everware/scripts/everware-server", "-f"]

