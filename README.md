#   INSTALLATION and INITIAL SETUP  #
Follow this guide to install and configure the manager for the first time on a
Debian system. Production runs on Ubuntu LTS.  

Start from bare metal on deb/ubuntu (do this in order):

    # apt-get install git mongodb-server nginx python2.7 python-dev python-setuptools gcc python-imaging python-gridfs  


python dependencies

    # easy_install python-dateutil python-daemon psutil lockfile pymongo pydns validate-email user-agents xlwt

Now, as the non-root user who is going to run the Manager's processes, do this:

    # exit
    $ cd
    $ git clone https://github.com/toconnell/kdm-manager.git 

Assuming that the user who wants to run the application is toconnell, and that 
you're ONLY using this server for kdm-manager, do this as root:

    # ln -s /home/toconnell/kdm-manager/v1/init_script /etc/init.d/kdm-manager  
    # update-rc.d -f kdm-manager defaults  
    # /etc/init.d/nginx stop
    # rm /etc/nginx/sites-enabled/default
    # ln -s /home/toconnell/kdm-manager/v1/nginx/default /etc/nginx/sites-enabled/kdm-manager_dev

The file /v1/nginx/production that ships with the repo contains all of the 
media (static content) server and redirect configs that facilitate the 
production deployment of the Manager. 

If you're just doing some dev/support work, you don't need all of that and you
should stick with /v1/nginx/default as your webserver config.

Restarting nginx and running the Manager's init script for the first time will
create the log and lockfile directories. it should also start the server on the
port specified in settings.cfg:

    # /etc/init.d/nginx start
    # /etc/init.d/kdm-manager start  


Following that, the Manager will be running and it should start automatically on
reboot.

Finally, please review the wiki for additional information on installation and
deployment, including troubleshooting tips: https://github.com/toconnell/kdm-manager/wiki
