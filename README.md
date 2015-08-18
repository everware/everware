
# Everware

In order to test `everware`, you can

 - Install the newest git version of Jupyterhub: https://github.com/jupyter/jupyterhub
 - Create a Github OAuth application with URL http://localhost:8000/ and callback URL http://localhost:8000/hub/oauth_callback
 - Clone this repo
 - Enter you OAuth information into `env.sh` and source it
 - While inside this repo, run

```
    $ pip install --user .
    $ jupyterhub
```

