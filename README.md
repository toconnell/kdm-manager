#   INSTALLATION and INITIAL SETUP  #
Follow this guide to install and configure the manager for the first time on a
Debian system. Production runs on Ubuntu LTS.  

Start from bare metal on deb/ubuntu (do this in order):

    # apt-get install python2.7 python-dev python-setuptools gcc python-imaging python-gridfs  
    # apt-get install git mongodb-server  
    # git clone ssh://toconnell@toconnell.info:222/~/git/kdm-manager  
    # apt-get install nginx  


python dependencies

    easy_install python-dateutil python-daemon psutil lockfile pymongo pydns validate-email user-agents xlwt

finally, as root, do this:

    # ln -s /home/toconnell/kdm-manager/v1/init_script /etc/init.d/kdm-manager  
    # update-rc.d -f kdm-manager defaults  
    # ln -s /home/toconnell/kdm-manager/v1/nginx/default kdm-manager_dev			# this makes kdm-manager the default webserver response  
    # /etc/init.d/kdm-manager start  

Running the init script for the first time should create the log and lockfile
directories. it should also start the server on the port in settings.cfg.  

Following that, the manager should start on system reboot.

#   Production deployment notes    #
If you plan to run the Manager in any kind of production context, e.g. where
you'll need to send password reset emails or do batch operations on users via the
REST API (e.g. get_user, etc.), you'll need to create a file called 
'settings_private.cfg' in the project root directory.

settings_private.cfg should look like this:

    [admin]
    key         = <your secret admin key here>

    [smtp]
    host        = <SMTP host here, e.g. smtp.whatever.com>
    name        = <SMTP user email address, e.g. admin@whatever.com>
    name_pretty = <SMTP user pretty name for subject line>
    pass        = <SMTP user password here>
    no-reply    = <no-reply email address, e.g. noreply@kdm-manager.com>

Finally, the manager should run perfectly fine without this file, but if you
experience tracebacks that point in the direction of these settings, just create
the file and populate it with dummy info and that should get you back up and
running.

(Let me know if that happens, though, because that's a bug.)

