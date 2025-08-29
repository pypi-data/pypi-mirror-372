QuartzBio Python Client
=======================

This is the QuartzBio Python package and command-line interface (CLI).


Installation & Setup
--------------------

Install `quartzbio` using `pip`:

    pip install quartzbio


For interactive use, we recommend installing `IPython` and `gnureadline`:

    pip install ipython
    pip install gnureadline


To log in, type:

    quartzbio login


Enter your QuartzBio credentials and you should be good to go!


Install from Git
----------------

    pip install -e git+https://github.com/quartzbio/quartzbio-python.git#egg=quartzbio


Development
-----------

    git clone https://github.com/quartzbio/quartzbio-python.git
    cd quartzbio-python/
    python setup.py develop

    or 

    pip install -e .


Or install `tox` and run:

    pip install tox
    tox


Releasing
---------

You will need to [configure Twine](https://twine.readthedocs.io/en/latest/#installation) in order to push to PyPI.

Maintainers can release quartzbio-python to PyPI with the following steps:

    bumpversion <major|minor|patch>
    git push --tags
    make changelog
    make release



Support
-------

For requests, please email QuartzBio Product Support.


Configuring the QuartzBio Client
-------

The QuartzBio python client can be configured by setting system environment variables.
Supported environment variables are:

`QUARTZBIO_API_HOST`     
- The URL of the target API backend. 
If not specified the value from the local credentials file will be used.

`QUARTZBIO_ACCESS_TOKEN` 
- The OAuth2 access token for authenticating with the API.

`QUARTZBIO_API_KEY`   
- The API Key to use for authenticating with the API. We strongly recommend using access tokens.

The lookup order for credentials is:
1. Access Token environment variable
2. API Key environment variable
3. Local Credentials file entry for the specific API host

`QUARTZBIO_LOGLEVEL` 
- The log level at which to log messages.
If not specified the default log level will be WARN.

`QUARTZBIO_LOGFILE`        
- The file in which to write log messages. 
If the file does not exist it will be created. 
If not specified '~/.quartzbio/quartzbio-python.log' will be used by default.

`QUARTZBIO_RETRY_ALL`
- Flag for enabling aggressive retries for failed requests to the API.
When truthy, the client will attempt to retry a failed request regardless of the type of operation.
This includes idempotent and nonidempotent operations:
"HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"
If this value is not set it will default to false and retries will only be enabled for idempotent operations.


Documentation
-------------

Project documentation is powered by Sphinx + Sphinx Autobuild.

To build the docs locally and view them in a browser:

    make sphinx-autobuild

