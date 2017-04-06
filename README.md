
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

 - install `nodejs` and `npm` (platform-specific)
 - create and activate a `conda` environment with python 3.5(or 3.6.0)
```
    conda create -n everware python=3.5
    source activate everware
```
 - Clone this repo and install `everware`
```
    git clone https://github.com/everware/everware
    cd everware
    make install
```
 - [Create a Github OAuth application](https://github.com/settings/applications/new)
   with URL `http://localhost:8000/` and callback URL
   `http://localhost:8000/hub/oauth_callback`
 - Enter you OAuth information into `env.sh` and `source env.sh`. You will
   have to set these environment variables every time before running `everware`

 - If you are on **Mac OS** make sure the VM in which docker runs is
   started (`docker-machine start <vm-name>`) and your environment is
   setup properly (`docker-machine env <vm-name>`). Start `everware` with:
```
    everware-server -f etc/local_dockermachine_config.py --debug --no-ssl
```
 - If you are on **Linux** make sure `dockerd` is running, your user 
   is in docker group and your environment contains the required 
   information (`DOCKER_HOST` is set, etc). Then start `everware` with
```
    everware-server -f etc/local_config.py --debug --no-ssl
```

Everware can also be deployed in a Docker container. See [Everware in Docker container](docker.md)


## Development

Follow the instructions for deploying your own everware instance. In
addition to run our tests you will need [selenium] and [firefox]. On
OS X you can install selenium with:

```
brew install selenium-server-standalone
```

_Note:_ if you are not starting from an environment that already contains
[dockerspawner] make sure it is updated to the right commit. `pip` will
be satisfied if it is installed which might leave you with an old version.


[selenium]: http://www.seleniumhq.org/
[jupyterhub]: https://github.com/jupyter/jupyterhub
[dockerspawner]: https://github.com/jupyter/dockerspawner
[firefox]: https://www.mozilla.org/en-US/firefox/

## More information

Slides (2016-10): https://speakerdeck.com/anaderi/everware-toolkit-supporting-reproducible-science-and-challenge-driven-education

Paper (2017-02): https://arxiv.org/abs/1703.01200