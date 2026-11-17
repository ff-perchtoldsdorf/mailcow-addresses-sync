#!/bin/bash
set -euo pipefail

cd /opt/mailcow-postfix-sync

/usr/bin/python3 main.py

/usr/sbin/postmap /etc/postfix/relay_recipients