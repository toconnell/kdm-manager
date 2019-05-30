#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo -e "\n\tThis script must be run as root!\n"
   exit 1
fi

#
#   Copies some symlinks; runs supervisorctl
#

SUPERVISORCTL=`which supervisorctl`
APP_ROOT=`pwd`

install() {
    echo -e " Creating symlinks:"
    ln -v -s $APP_ROOT/supervisor.conf /etc/supervisor/conf.d/kdm-manager.conf
    ln -v -s $APP_ROOT/nginx.conf /etc/nginx/sites-enabled/kdm-manager
    echo -e "\n Reloading services:"
    /etc/init.d/nginx reload
    $SUPERVISORCTL reload
    sleep 5
    tail /var/log/supervisor/supervisord.log
    echo -e ""
    netstat -anp |grep "0.0.0.0"
    echo -e "\n Done!\n"
}

echo -e "\n\tKDM-Manager! Installer"
read -sn 1 -p "
 Press any key to create links to $APP_ROOT/deploy files...
";echo

install
