#!/bin/bash

#
#	params
#

INSTALL_USER=toconnell	# the user who will run the Manager (cannot be root)
INSTALL_TYPE=dev	# removes the default nginx server config
#INSTALL_TYPE=prod	# not recommended; used only in production
LOGGING_ROOT=/var/log/kdm-manager
PID_FILE_DIR=/var/run/kdm-manager
NGINX_ROOT_D=/etc/nginx
APP_PORT_NUM=8012
API_IP_ADDR=`hostname -I`
#API_IP_ADDR=192.168.0.110  # hardcode this if hostname -I misbehaves (e.g. multuple NICs)
API_PORT_NUM=8013   # do not change this unless you know what you're doing!


###	DO NOT EDIT BELOW THIS LINE ###


SYSTEMCTL=`which systemctl`
INSTALL_USER_HOME=`eval echo "~$INSTALL_USER"`
INSTALL_DIR=$INSTALL_USER_HOME/kdm-manager

#
#	functions
#

# 	install

do_create_init_script () {

	# this one does the old Marty Walsh 'cat stubs into a single file'
	# routine to create an init script with installation-specific values

	printf "Creating new init script..."

	# first create it
	INIT_SCRIPT=$INSTALL_DIR/v1/init
	cat $INSTALL_DIR/v1/files/init_script_top > $INIT_SCRIPT
	echo "USERNAME=$INSTALL_USER" >> $INIT_SCRIPT
	echo "APP_ROOT_DIR=$INSTALL_DIR" >> $INIT_SCRIPT
	echo "LOG_ROOT_DIR=$LOGGING_ROOT" >> $INIT_SCRIPT
	echo "PID_ROOT_DIR=$PID_FILE_DIR" >> $INIT_SCRIPT
	cat $INSTALL_DIR/v1/files/init_script_bod >> $INIT_SCRIPT

    echo "done."

}

do_install_init_script () {

    # this is serparte from do_create_init_script so that we can refresh
    # the init script if necessary. This one also enables the systemd service
    # and starts the server.

	chown $INSTALL_USER: $INIT_SCRIPT
	chmod +x $INIT_SCRIPT

	# then link it and systemd enable it
	ln -s $INIT_SCRIPT /etc/init.d/kdm-manager -v
    $SYSTEMCTL enable kdm-manager
    $SYSTEMCTL start kdm-manager
	
}


do_update_settings_cfg () {
	
	# in which we update the generic settings.cfg in the root project dir

	UPDATE_SETTINGS=$INSTALL_DIR/v1/update_settings.py
	$UPDATE_SETTINGS application log_dir $LOGGING_ROOT/
	$UPDATE_SETTINGS application static_root $INSTALL_USER_HOME/media.kdm-manager.com/
	$UPDATE_SETTINGS api localhost_addr $API_IP_ADDR
	$UPDATE_SETTINGS api localhost_port $API_PORT_NUM
	$UPDATE_SETTINGS server pid_file $PID_FILE_DIR/server.pid
	$UPDATE_SETTINGS server port $APP_PORT_NUM
	$UPDATE_SETTINGS server uid `id -u $INSTALL_USER`
	$UPDATE_SETTINGS server gid `id -g $INSTALL_USER`
	$UPDATE_SETTINGS server nginx_config $NGINX_ROOT_D/sites-enabled/kdm-manager

    sleep 1

    cp $INSTALL_DIR/v1/files/settings_private_stub $INSTALL_DIR/v1/settings_private.cfg -v

}


do_dev_install () {
    echo "kdm-manager will be the default server in NGINX"
	ln -s $INSTALL_DIR/v1/nginx/default $NGINX_ROOT_D/sites-enabled/default -v
}
do_prod_install () {
	ln -s $INSTALL_DIR/v1/nginx/kdm-manager $NGINX_ROOT_D/sites-enabled/kdm-manager -v
}

do_install () {

	# calls all of the sub-functions that constitute our installation

    echo ""
	do_create_init_script
    echo "Installing init script and starting server..."
    do_install_init_script
    echo "CGI server 0.0.0.0:$APP_PORT_NUM has PID `cat $PID_FILE_DIR/server.pid`"

	printf "Updating settings.cfg..."
	do_update_settings_cfg
    rm /etc/nginx/sites-enabled/default -v

    case "$INSTALL_TYPE" in
        dev)
            do_dev_install
        ;;
        prod)
            do_prod_install
        ;;
    *)
        echo "UNKNOWN INSTALL TYPE. FAIL."
        exit 3
    esac

    echo "Installing API server..."
	ln -s $INSTALL_DIR/v2/api/nginx/production $NGINX_ROOT_D/sites-enabled/api.thewatcher.io -v
    mkdir -v $INSTALL_DIR/v2/api/log
    chown -vR $INSTALL_USER: $INSTALL_DIR/v2/api/log
    mkdir -v $INSTALL_DIR/v2/api/run
    chown -vR $INSTALL_USER: $INSTALL_DIR/v2/api/run
    API_PRIV_SETTINGS=$INSTALL_DIR/v2/api/settings_private.cfg
    touch $API_PRIV_SETTINGS
    echo -e "[api]\nsecret_key = USE A SECURE VALUE IN PRODUCTION" > $API_PRIV_SETTINGS
    $INSTALL_DIR/v2/api/server.sh enable
    $INSTALL_DIR/v2/api/server.sh start

    # start the world daemon, refresh it and dump status
    su - $INSTALL_USER -c "cd $INSTALL_DIR/v2/api/ && ./world.py -d start"
#    su - $INSTALL_USER -c "cd $INSTALL_DIR/v2/api/ && ./world.py -r"
    cd $INSTALL_DIR/v2/api/ && ./world.py -d status 

    /etc/init.d/nginx reload

	echo -e "\n Installation complete! \n\n"
    
}


#	initialize

do_initialize () {

	# initializes variables used by the other functions in this section,
	# i.e. the ones that do the installing

	INITIALIZED=False

	echo -e "\n\t\e[1mINSTALLATION PARAMETERS\e[0m\n"
	echo -e " installation type = \e[93m$INSTALL_TYPE\e[0m"
	echo -e " install user name = \e[93m$INSTALL_USER (`id -u $INSTALL_USER`/`id -g $INSTALL_USER`)\e[0m"
	echo -e " source directory  = \e[93m$INSTALL_DIR\e[0m"
	echo -e " main app port     = \e[93m$APP_PORT_NUM\e[0m"
	echo -e " API server address= \e[93m$API_IP_ADDR\e[0m"
	echo -e " API server port   = \e[93m$API_PORT_NUM\e[0m"
	echo -e " webapp logger dir = \e[93m$LOGGING_ROOT\e[0m"
	echo -e " PID/lock file dir = \e[93m$PID_FILE_DIR\e[0m"
	echo -e " nginx install dir = \e[93m$NGINX_ROOT_D\e[0m"
	echo -e ""
    echo -e " \e[91mProceeding with this installation will reload NGINX.\e[0m\n"

	read -r -p " Install with the above parameters? [y/N] " response
	if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
	then
	    INITIALIZED="True"
	else
	    echo -e "\n Installation aborted by user. Exiting...\n"
		exit 1
	fi
}




#
#	run time!
#

# sanity check ; initialize; install

if [ $EUID -ne 0 ]; then
	echo -e "\n This script must be run as root!\n" 
    exit 1
fi

if [ $# -eq 1 ]; then
    case "$1" in
        init_script)
            do_create_init_script
            exit 0
            ;;
        remove)

            # server first
            $SYSTEMCTL stop kdm-manager
            $SYSTEMCTL disable kdm-manager
            rm $INSTALL_DIR/v1/init -v
            rm -rvf $PID_FILE_DIR
            rm -rvf $LOGGING_ROOT
            rm $NGINX_ROOT_D/sites-enabled/default
	        ln -s $NGINX_ROOT_D/sites-available/default $NGINX_ROOT_D/sites-enabled/default -v

            # then remove API
            cd $INSTALL_DIR/v2/api/ && ./world.py -d stop
            rm $NGINX_ROOT_D/sites-enabled/api.thewatcher.io
            $INSTALL_DIR/v2/api/server.sh disable

            # reload nginx
            /etc/init.d/nginx reload
            exit 0
            ;;
        *)
            echo -e "\n The only supported argument to $0 is 'remove':\n\n  $0 remove\n\n"        
            exit 1
    esac
fi

run_modes=["dev","prod"]

if [[ ${run_modes[*]} =~ $INSTALL_TYPE ]]; then

	do_initialize

	if [[ $INITIALIZED -eq "True" ]]; then
		do_install
	else
		echo -e "\n Could not initialize installer. Exiting...\n"
		exit 1
	fi

else
	echo -e "\n '$INSTALL_TYPE' is not a valid installation type. Exiting...\n"
	exit 1
fi


