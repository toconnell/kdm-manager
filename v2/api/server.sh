#!/bin/sh

PROJECT_ABS_PATH=/home/toconnell/kdm-manager/v2/api/
SERVICE=api.thewatcher.service
SOCKET=api.thewatcher.socket
SYSLOG=/var/log/syslog
CMD=`which systemctl`

cd $PROJECT_ABS_PATH
echo "Working directory set to `pwd` "

case "$1" in
    enable)
        $CMD enable $PROJECT_ABS_PATH$SERVICE
        $CMD enable $PROJECT_ABS_PATH$SOCKET
        ;;
    disable)
        $CMD stop $SERVICE
        $CMD stop $SOCKET
        $CMD disable $SERVICE
        $CMD disable $SOCKET
        ;;
	start)
        printf "Starting..."
        $CMD start $SERVICE
        $CMD start $SOCKET
        echo "done."
        ;;
	stop)
        $CMD stop $SERVICE
        $CMD stop $SOCKET
        ;;
	restart)
		$CMD restart $SERVICE
		$CMD restart $SOCKET
        ;;
	status)
		$CMD status $SERVICE
		$CMD status $SOCKET
        ;;
	*)
		echo "Usage: $NAME {enable|disable|start|stop|restart|status}" >&2
		exit 3
esac

sleep 3
echo "\n\tsystemctl output is logged to /var/log/syslog\n"
tail -n 15 $SYSLOG
echo "...\n"

