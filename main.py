import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

MAILCOW_URL = os.environ["MAILCOW_URL"]
MAILCOW_API_KEY = os.environ["MAILCOW_API_KEY"]
POSTFIX_RECIPIENT_FILE = os.environ["POSTFIX_RECIPIENT_FILE"]

def main():

    # check if .env vars set
    if not MAILCOW_URL or not MAILCOW_API_KEY or not POSTFIX_RECIPIENT_FILE:
        print("Error: MAILCOW_URL, MAILCOW_API_KEY and POSTFIX_RECIPIENT_FILE must be set in the .env file.")
        return
    else:

        # define Variables
        mailboxes = []
        aliases = []
        allowed_addresses = []
        ignored_addresses = []

        # get addresses
        try:
            mailboxes = get_mailboxes()
            aliases = get_aliases()
        except:
            print("Error while fetching")
            sys.exit(1)

        # add addresses to list
        for mailbox in mailboxes:
            allowed_addresses.append(mailbox["username"])

        for alias in aliases:
            if alias["internal"] == 0:
                allowed_addresses.append(alias["address"])
            else:
                ignored_addresses.append(alias["address"])

        # safe in file
        try:
            with open(POSTFIX_RECIPIENT_FILE, "w", encoding="utf-8") as f:
                for address in allowed_addresses:
                    print(f'{address} OK', file=f)
        except OSError as e:
            print(f"Error while writing file to {POSTFIX_RECIPIENT_FILE}: {e}")
            sys.exit(1)

        # Show Stats
        print("-- Addresses --")
        print("Allowed:", len(allowed_addresses))
        print("Ignored:", len(ignored_addresses))
        print()
        print("-- Ignored addresses --")
        for ignored in ignored_addresses:
            print(ignored)
    pass

def get_mailboxes():
    url = f"{MAILCOW_URL}/api/v1/get/mailbox/all"
    headers = {
        "X-API-Key": MAILCOW_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise SystemExit("Error while fetching Mailboxes")

def get_aliases():
    url = f"{MAILCOW_URL}/api/v1/get/alias/all"
    headers = {
        "X-API-Key": MAILCOW_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise SystemExit("Error while fetching Mailboxes")

# init
if __name__ == "__main__":
    main()