#!/bin/bash
echo "Content-type: text/plain"
echo ""

command=$(echo "$PATH_INFO" | sed 's/\///' | awk '{print $1}')
[[ -z "$command" ]] && command="stop"

/usr/bin/python3 /var/www/cgi-bin/car_control.py "$command"
