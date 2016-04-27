FROM jupyter/jupyterhub:0.5.0

COPY . /srv/everware
WORKDIR /srv/everware/
RUN make install

EXPOSE 8000
EXPOSE 8081

ENTRYPOINT ["/srv/everware/scripts/everware-server", "-f"]

