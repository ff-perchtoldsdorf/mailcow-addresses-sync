#!/bin/sh
set -eu
# Postfix SMTP delivery runs chrooted and needs the host DNS configuration.
mkdir -p /var/spool/postfix/etc
cp /etc/resolv.conf /var/spool/postfix/etc/resolv.conf

# The map must exist before Postfix starts. The sync container replaces it later.
if [ ! -f /var/lib/postfix-sync/relay_recipients.db ]; then
    touch /var/lib/postfix-sync/relay_recipients
    postmap /var/lib/postfix-sync/relay_recipients
fi
exec postfix start-fg
