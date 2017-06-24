#!/bin/sh

PROJECT_ABS_PATH=/home/toconnell/kdm-manager/v2/api/
WORLD_DAEMON=/home/toconnell/kdm-manager/v2/api/world.py
SERVICE=api.thewatcher.service
SOCKET=api.thewatcher.socket
SYSLOG=/var/log/syslog
CMD=`which systemctl`

cd $PROJECT_ABS_PATH
echo "Working directory set to `pwd` "


start_service () {
    $CMD start $SOCKET
    $CMD start $SERVICE
    su - toconnell -c "$WORLD_DAEMON -d start"
    sleep 2
    su - toconnell -c "$WORLD_DAEMON -d status"
}

stop_service () {
    su - toconnell -c "$WORLD_DAEMON -d stop"
    $CMD stop $SERVICE
    $CMD stop $SOCKET
}


case "$1" in
    enable)
        $CMD enable $PROJECT_ABS_PATH$SERVICE
        $CMD enable $PROJECT_ABS_PATH$SOCKET
        ;;
    disable)
        stop_service
        $CMD disable $SERVICE
        $CMD disable $SOCKET
        ;;
	start)
        start_service
        ;;
	stop)
        stop_service
        ;;
	restart)
        stop_service
        start_service
        ;;
	status)
		$CMD status $SERVICE
		$CMD status $SOCKET
        ;;
	*)
		echo "Usage: $NAME {enable|disable|start|stop|restart|status}" >&2
		exit 3
esac


#sleep 3
#echo "\n\tsystemctl output is logged to /var/log/syslog\n"
#tail -n 15 $SYSLOG
#echo "...\n"

