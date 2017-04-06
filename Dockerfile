FROM jupyterhub/jupyterhub:0.7.2
RUN apt-get update && apt-get install make

COPY . /srv/everware
WORKDIR /srv/everware/
RUN cd $(npm root -g)/npm && npm install fs-extra \
	&& sed -i -e s/graceful-fs/fs-extra/ -e s/fs.rename/fs.move/ ./lib/utils/rename.js
RUN make clean install

EXPOSE 8000
EXPOSE 8081

ENTRYPOINT ["/srv/everware/scripts/everware-server", "-f"]

