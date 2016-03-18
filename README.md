
# everware

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/everware/everware)
[![Build Status](https://travis-ci.org/everware/everware.svg?branch=master)](https://travis-ci.org/everware/everware)

**Everware is about re-useable science, it allows people to jump right
in to your research code.**

It lets you launch [Jupyter](https://jupyter.org) notebooks from a git
repository with a click of a button. Everware is an extension for
[JupyterHub]. The main component is a spawner that allows you to spawn
custom docker images.

Checkout the **[ROADMAP](../../issues/39)** to see where we are going
and how to get involved with the project.

See [this blog
post](http://betatim.github.io/posts/project-everware-reusable-science/)
for more information about what `everware` is and how it can be useful.

The idea for everware originated at the CERN Webfest 2015.  The
original everware team consists of
[@OmeGak](https://github.com/omegak),
[@ibab](https://github.com/ibab), [@ndawe](https://github.com/ndawe),
[@betatim](https://github.com/betatim),
[@uzzielperez](https://github.com/uzzielperez),
[@anaderi](https://github.com/anaderi), and
[@AxelVoitier](https://github.com/AxelVoitier).

## Documentation

We have some documentation on the different ways to use `everware` and
[getting
started](https://github.com/everware/everware/wiki/Getting-Started).

## Try it out

In order to deploy your own `everware` instance, you have to:

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
 - [Create a Github OAuth application](https://github.com/settings/applications/new) with URL `http://localhost:8000/` and callback URL `http://localhost:8000/hub/oauth_callback`
 - Enter you OAuth information into `env.sh` and `source env.sh`
 - Install everware
```
    pip3 install -e .
```
 - If you are not using `boot2docker`, but run directly on Linux, edit `jupyterhub_config.py` as indicated in the file.
 - Run
```
    jupyterhub
```

## Development

To run our tests you will need [selenium] and [phantomjs]. On OS X you can install them with:

```
brew install selenium-server-standalone
brew install phantomjs
```

## Final remarks

if you aren't starting from a clean env, make sure [dockerspawner] is new enough

[selenium]: http://www.seleniumhq.org/
[phantomjs]: http://phantomjs.org/
[jupyterhub]: https://github.com/jupyter/jupyterhub
[dockerspawner]: https://github.com/jupyter/dockerspawner