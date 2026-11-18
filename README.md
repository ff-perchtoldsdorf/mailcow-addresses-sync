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