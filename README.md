# [https://kdm-manager.com](https://kdm-manager.com)
* Webapp: [AngularJS](https://angularjs.org/) (1.5.4)
* Webserver: [Gunicorn](http://gunicorn.org/)
* API: [Flask](http://flask.pocoo.org/)

## Introduction 
[https://kdm-manager.com](https://kdm-manager.com) or, as it is generally called, the Manager, is an Interactive campaign manager for *Monster* by [Kingdom Death](https://kingdomdeath.com).

Neither the [https://kdm-manager.com](https://kdm-manager.com) service nor any of the software utilized by that service are developed, maintained, authorized or in any other way supported by or affiliated with Kingdom Death or Adam Poots Games, LLC.

The Manager (including the API at [https://thewatcher.io](https://thewatcher.io)) is not affiliated or acknowledged in any way, shape or form by Kingdom Death. Both the Manager and the API are independent, fan-maintained projects.

For more information, please refer to [the project's development blog](http://kdm-manager.blogspot.com/p/credits-and-acknowledgements.html).



#   INSTALLATION and INITIAL SETUP
Follow this guide to install and configure the Manager and the KDM API on a
Debian system. 

For the time-being, the Manager and the API are tightly coupled and it is highly recommended to install and develop for both simultaneously.

Both [https://kdm-manager.com](https://kdm-manager.com) and [https://thewatcher.io](https://thewatcher.io) run on Ubuntu 16.04 LTS.


## 1.) Install Dependencies 

If your goal is to start from bare metal on a deb/ubuntu system, you will need
to install the following packages:

    ~# apt-get install git mongodb-server nginx python2.7 python-dev python-setuptools gcc python-imaging python-gridfs


python dependencies (PIP should work for all of these if you've moved from `easy_install`)

    ~# easy_install python-dateutil python-daemon=2.1.1 psutil lockfile pymongo pydns validate-email user-agents xlwt requests flask flask_jwt flask-jwt-extended retry gunicorn

**Important!** If you have installed the normal jwt package (e.g. via *easy_install*
or *pip*) and experience issues running the Manager, open an issue in GitHub and
let me know.

As the non-root user who is going to run the Manager's processes, do this:

    ~# exit
    ~$ cd
    ~$ git clone https://github.com/toconnell/kdm-manager.git 

Now that you've got all of the prerequisites in place, you are ready to run the
`install.sh` script in the project root directory.


## 2.) Install the Manager and the API

First, review the `install.sh` script in the root of the kdm-manager folder and
set the parameters according to the instructions provided.

Then, as root, run the script:

	root@mona:/home/toconnell/kdm-manager# ./install.sh

Assuming that you chose the *dev* install type, the Manager is now the default 
server and if you point your browser at it, you should be good to go.

If you chose the *prod* install type, your NGINX sites-enabled directory has a
symlink to the v1/nginx/production config and has been reloaded to include it.


## Administration

The `install.sh` script installs two *systemd* services, `kdm-manager` (i.e. the
CGI server/webapp) and `api.thewatcher.service`, which must both be running for
the Manager to work properly.

The API, however, does not require the `kdm-manager` service, and you may choose
to stop/disable it using regular `systemctl` syntax:

    # systemctl stop kdm-manager
    # systemctl disable kdm-manager

Both services will start when the system starts, unless disabled.


# Additional Resources

The headings below provide links to other development/administration resources
for both the Manager and the KDM API.

## General Development

Please review the [Github wiki pages](https://github.com/toconnell/kdm-manager/wiki)
for additional information on installation and deployment, including
troubleshooting tips.

The [kdm-manager Development Blog](http://blog.kdm-manager.com) contains detailed
release notes for every production release of the manager and the KDM API.

## API Development

The KDM API has built-in documentation. The production release of that documentation
will always be available at [api.thewatcher.io](http://api.thewatcher.io)

## Contact the Author

The Manager and the API are, for now, maintained by a single individual. For more information, including how to get involved in the project, please contact:

* Timothy O'Connell [toconnell@tyrannybelle.com](mailto:toconnell@tyrannybelle.com) <br />
  Designer, full-stack developer and maintainer. <br />
  http://toconnell.info

