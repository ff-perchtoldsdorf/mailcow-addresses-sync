#!/bin/sh
set -eu
# The map must exist before Postfix starts. The sync container replaces it later.
if [ ! -f /var/lib/postfix-sync/relay_recipients.db ]; then
    touch /var/lib/postfix-sync/relay_recipients
    postmap /var/lib/postfix-sync/relay_recipients
fi
exec postfix start-fg
