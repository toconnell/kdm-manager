#!/bin/bash

systemctl enable /home/toconnell/kdm-manager/v2/api/api.thewatcher.service
systemctl enable /home/toconnell/kdm-manager/v2/api/api.thewatcher.socket
systemctl start api.thewatcher.service
systemctl start api.thewatcher.socket

echo "systemd installation complete."
