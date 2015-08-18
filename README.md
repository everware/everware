
# everware

Everware is an add-on for [JupyterHub](https://github.com/jupyter/jupyterhub).
It allows users to launch [Jupyter Notebooks](https://github.com/jupyter/notebook.git) into a docker container simply by specifying the url of a git repository.
Everware clones the repository, builds a docker image from a contained `Dockerfile` and launches the user into a running notebook instance inside the container.

Everware is designed to be a tool for [Open Science](https://en.wikipedia.org/wiki/Open_science).
If a researcher provides an everware-compatible public git repository, it's possible to verify their research by simply launching the repository inside everware.

See [this blog post](http://betatim.github.io/posts/project-everware-reusable-science/) for more information about what everware is and how it can be useful.

The idea for everware originated at the CERN Webfest 2015.
The original everware team consists of [@OmeGak](https://github.com/omegak), [@ibab](https://github.com/ibab), [@ndawe](https://github.com/ndawe), [@betatim](https://github.com/betatim), [@uzzielperez](https://github.com/uzzielperez), [@anaderi](https://github.com/anaderi), and [@AxelVoitier](https://github.com/AxelVoitier).

## Testing

In order to test `everware`, you have to:

 - Install the newest git version of `jupyterhub`: https://github.com/jupyter/jupyterhub. Double check with their [README.md](https://github.com/jupyter/jupyterhub/blob/master/README.md)
```
    sudo apt-get install npm nodejs-legacy
    sudo npm install -g configurable-http-proxy
    git clone https://github.com/jupyter/jupyterhub.git
    cd jupyterhub
    pip3 install -r dev-requirements.txt -e .
```
 - Install the newest git version of `dockerspawner`: https://github.com/jupyter/dockerspawner. Double check with their [README.md](https://github.com/jupyter/dockerspawner/blob/master/README.md)
```
    git clone https://github.com/jupyter/dockerspawner.git
    cd dockerspawner
    pip3 install -e .
```
 - Clone this repo
```
    git clone https://github.com/everware/everware
    cd everware
```
 - Create a Github OAuth application with URL `http://localhost:8000/` and callback URL `http://localhost:8000/hub/oauth_callback`
 - Enter you OAuth information into `env.sh` and `source env.sh`
 - Run
```
    pip3 install -e .
    jupyterhub
```

