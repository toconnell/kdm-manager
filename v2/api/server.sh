#!/bin/sh

CMD=`which systemctl`
PROJECT_ABS_PATH=/home/toconnell/kdm-manager/v2/api/
SERVICE=api.thewatcher.service
SOCKET=api.thewatcher.socket


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
        $CMD start $SERVICE
        $CMD start $SOCKET
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
