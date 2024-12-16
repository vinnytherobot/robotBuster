#!/usr/bin/env python3

import os
import requests
import argparse
import pyfiglet
from pytz import timezone
from datetime import datetime
from threading import Thread

class Colors:
    INFO = "\033[34m"
    SUCCESS = "\033[32m"
    ERROR = "\033[31m"
    WARNING = "\033[33m"
    RESET = "\033[m"

def clear_screen():
    os.system("clear")

def print_header():
    print("Developed by: vinnytherobot")
    print("Beta v1.0")
    print("Code: https://github.com/vinnytherobot/robotBuster")
    print("Profile Github: https://github.com/vinnytherobot")
    sleep(0.5)
    banner = pyfiglet.figlet_format("VINNYROBOT")
    print(Colors.SUCCESS + banner + Colors.RESET)

def print_message(text="", message_type="info"):
    date_and_hour_now = datetime.now().astimezone(timezone("Europe/London")).strftime("%H:%M:%S")

    message_color = {
        "info": Colors.INFO,
        "finished": Colors.SUCCESS,
        "error": Colors.ERROR,
        "warning": Colors.WARNING
    }.get(message_type, "")

    print(f"[{Colors.INFO}{date_and_hour_now}{Colors.RESET}] [{message_color}{message_type.upper()}{Colors.RESET}] {text}")

def send_request(url):
    try:
        return requests.get(url)
    except requests.exceptions.RequestException as e:
        print_message(f"Error sending request: {e}", "error")
        return None

def search():
    url = args.url
    wordlist = args.wordlist
    found_routes = []

    try:
        with open(wordlist, "r") as file:
            for route in file:
                route = route.strip()
                request = send_request(url + route)

                if request and request.status_code == 200:
                    found_routes.append(route)
                    print_message(f"Directory found: {request.url}", "info")

    except KeyboardInterrupt:
        print_message("\nExiting... Goodbye", "error")
        exit()
    except FileNotFoundError:
        print_message(f"Wordlist file '{wordlist}' not found", "error")
        exit()

    print_message(f"Finished with {len(found_routes)} results!", "finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Directory searcher")
    parser.add_argument("-u", "--url", required=True, type=str, help="specify a target URL")
    parser.add_argument("-w", "--wordlist", required=True, type=str, help="specifies a wordlist to search")
    parser.add_argument("-v", "--version", action="version", version="v1.0", help="show tool version and exit")

    args = parser.parse_args()

    clear_screen()
    print_header()

    if args.url and args.wordlist:
        Thread(target=search).start()
