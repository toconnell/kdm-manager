#!/bin/bash

systemctl stop api.thewatcher.service
systemctl stop api.thewatcher.socket
systemctl disable api.thewatcher.service
systemctl disable api.thewatcher.socket
systemctl enable /home/toconnell/kdm-manager/v2/api/api.thewatcher.service
systemctl enable /home/toconnell/kdm-manager/v2/api/api.thewatcher.socket
systemctl start api.thewatcher.service
systemctl start api.thewatcher.socket

echo "Done."
