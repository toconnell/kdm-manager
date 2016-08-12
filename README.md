#   INSTALLATION and INITIAL SETUP  #
Follow this guide to install and configure the manager for the first time on a
Debian system. Production runs on Ubuntu LTS.

# Start from bare metal on deb/ubuntu (do this in order):
apt-get install python2.7 python-dev python-setuptools gcc python-imaging python-gridfs  
apt-get install git mongodb-server  
git clone ssh://toconnell@toconnell.info:222/~/git/kdm-manager  
apt-get install nginx  


    # python dependencies

easy_install python-dateutil python-daemon psutil lockfile pymongo pydns validate-email user-agents xlwt

    # finally, as root:
ln -s /home/toconnell/kdm-manager/v1/init_script /etc/init.d/kdm-manager  
update-rc.d -f kdm-manager defaults  
ln -s /home/toconnell/kdm-manager/v1/nginx/default kdm-manager_dev			# this makes kdm-manager the default webserver response  
/etc/init.d/kdm-manager start  

    # running the init script for the first time should create the log and lockfile
    # directories. it should also start the server on the port in settings.cfg
    #
    # following that, the manager should start on system reboot


