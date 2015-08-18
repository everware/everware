
# Everware

Everware is an add-on for [JupyterHub](https://github.com/jupyter/jupyterhub).
It allows users to launch [Jupyter Notebooks](https://github.com/jupyter/notebook.git) into a docker container simply by specifying the url of a git repository.
Everware clones the repository, builds a docker image from a contained `Dockerfile` and launches the user into a running notebook instance inside the container.

Everware is designed to be a tool for [Open Science](https://en.wikipedia.org/wiki/Open_science).
If a researcher provides an everware-compatible public git repository, it's possible to verify their research by simply launching the repository inside everware.

See [this blog post](http://betatim.github.io/posts/project-everware-reusable-science/) for more information about what everware is and how it can be useful.

The idea for everware originated at the CERN Webfest 2015.
The original everware team consists of @OmeGak, @ibab, @ndawe, @betatim, @uzzielperez, @anaderi, and @AxelVoitier.

# Testing

In order to test `everware`, you can

 - Install the newest git version of Jupyterhub: https://github.com/jupyter/jupyterhub
 - Create a Github OAuth application with URL `http://localhost:8000/` and callback URL `http://localhost:8000/hub/oauth_callback`
 - Clone this repo
 - Enter you OAuth information into `env.sh` and source it
 - Run

```
    $ pip install --user .
    $ jupyterhub
```

