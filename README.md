# Mailcow relay recipients exporter for Postfix
This script generates a relay_recipients for postfix relay servers

## Setup
### Linux
1. Clone repo and install packages
```bash
apt update
apt install -y python3 python3-requests python3-dotenv git

cd /opt
git clone https://github.com/ff-perchtoldsdorf/mailcow-addresses-sync.git mailcow-postfix-sync
cd mailcow-postfix-sync
cp .env.example .env
```
2. Change the variables in `.env`
3. Setup cron job
```bash
sudo crontab -e
```
```text
*/5 * * * * /usr/bin/flock -n /run/mailcow-postfix-sync.lock /opt/mailcow-postfix-sync/sync.sh >> /var/log/mailcow-postfix-sync.log 2>&1
```
4. Add map to Postfix config `/etc/postfix/main.cf`
```text
relay_recipient_maps = hash:/etc/postfix/relay_recipients
```
5. Reload Postfix
```bash
sudo postfix check
sudo systemctl reload postfix
```

## Develop
```bash
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
python main.py
```
## Docker

The release workflow publishes the sync image to GitHub Container Registry as
`ghcr.io/<owner>/<repository>:<release-tag>`; stable releases also update
`latest`. The package must be public for anonymous pulls, otherwise authenticate
with `docker login ghcr.io` using an account with package access.

1. In `docker`, copy `.env.example` to `.env` and enter your Mailcow URL, API key and reachable IPv4 address in `MAILCOW_IP`.
   `SYNC_INTERVAL` is in seconds. Keep `POSTFIX_RECIPIENT_FILE` at the example
   path unless you also change the matching Postfix configuration and volume.
2. Edit `docker/postfix/main.cf`: set `myhostname`, `relay_domains`, and the
   Mailcow destination in `relay_transport`. Add only the source IP of Mailcow to `mynetworks` (for example `192.0.2.10/32`). This example accepts mail for the
   configured relay domains and checks recipients against the synchronized map.
3. Run `docker compose up -d --build` from the `docker` directory. The sync
   container pulls the published image; Postfix is built locally and HAProxy uses the official image. Adjust the
   image name in `docker-compose.yml` if the repository is renamed or forked.
4. Check `docker compose logs -f`. Postfix uses Linux host networking and listens
   on host port 25. Ensure the port is free and accessible. The Postfix configuration and generated maps are
   stored in `docker/postfix` on the host. After changing `main.cf`, run
   `docker compose restart postfix`.

Until the first successful sync, the recipient map is empty and mail for relay
recipients is rejected. The last successful map is kept if a later sync fails.
The example is a starting configuration: configure DNS, TLS and any additional
mail policies for your environment before exposing it to the internet.

For outgoing mail, configure Mailcow to use this relay host on port 25. The IP
in `mynetworks` must be the actual source IP seen by Postfix, including any NAT.
Do not trust a Docker bridge or proxy address shared by other clients: that
would permit them to relay mail too. Confirm with an SMTP test that Mailcow is
accepted and an untrusted external client cannot relay to an unrelated domain.
Messages to other domains are delivered directly using DNS MX records; outgoing
TCP port 25, correct DNS, PTR, SPF and DKIM are needed for reliable delivery.
The Postfix queue is stored in the `postfix-queue` Docker volume. Host networking
is intended for Linux Docker Engine; Docker Desktop networking differs and this
example must not be used there without verifying source IP preservation.
HAProxy uses `docker/haproxy/haproxy.cfg` and forwards TCP ports 465, 587,
993, 995, 4190, 443 and 80 to `MAILCOW_IP` on the same ports. Port 25 remains
with Postfix. The HTTP and HTTPS backends send PROXY protocol v2, as in the
original configuration: the Mailcow web server must be configured to accept it
and trust this proxy. The mail protocol backends do not send the PROXY protocol,
so Mailcow sees the proxy as the client for those connections. TLS is passed
through to Mailcow. HAProxy logs to `docker compose logs haproxy`.

Both HAProxy and Postfix use host networking on Linux; make sure their ports
are available and the host can reach the Mailcow IP (including over a VPN, if
applicable). After changing `MAILCOW_IP` in `.env`, recreate HAProxy with
`docker compose up -d --force-recreate haproxy`. After editing its config,
validate it with `docker compose exec haproxy haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg`
and then restart it with `docker compose restart haproxy`.