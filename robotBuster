#!/usr/bin/env python3

import os
import requests
import argparse
import pyfiglet
from pytz import timezone
from time import sleep
from datetime import datetime
from threading import Thread

parser = argparse.ArgumentParser(description="Directory searcher")

parser.add_argument("-u", "--url", required=True, type=str, help="specify a target url")
parser.add_argument("-w", "--wordlist", required=False, type=str, help="specifies a wordlist to search.")
parser.add_argument("-v", "--version", action="version", version="v1.0", help="show tool version and exit.")

args = parser.parse_args()

def start():
    os.system("clear")
    print("Developed by: vinnyrobot")
    print("Beta v1.0")
    print("Code: https://gitbub.com/vinnyrobot/robotBuster")
    print("Profile Github: https://github.com/vinnyrobot")
    sleep(0.5)
    banner = pyfiglet.figlet_format("VINNYROBOT")
    print("\033[1;32m" + banner + "\033[m")


def message(text="", messageType=""):
    dateAndHourNow = datetime.now()
    timeZone = timezone("Europe/London")
    dateAndHourLondon = dateAndHourNow.astimezone(timeZone)
    dateAndHourLondonInText = dateAndHourLondon.strftime("%H:%M:%S")

    if messageType == "info":
        print("[\033[34m" + dateAndHourLondonInText + "\033[m]", "[\033[32m" + "INFO" + "\033[m]", str(text))
    elif messageType == "finished":
        print("\n[\033[34m" + dateAndHourLondonInText + "\033[m]", "[\033[32m" + "FINISHED" + "\033[m]", str(text))
    elif messageType == "error":
        print("[\033[31m" + "ERROR" + "\033[m]", str(text))
    elif messageType == "warning":
        print("[\033[34m" + dateAndHourLondonInText + "\033[m]", "[\033[33m" + "WARNING" + "\033[m]", str(text))
    else:
        print(text)


def sendRequest(url):
    request = requests.get(url)

    return request


def search(url, wordlist):
    foundRoutes = []
    try:

        file = open(wordlist)
        for route in file.readlines():
            request = sendRequest(url + str(route).replace("\n", ""))

            if request.status_code == 200:
                message("Directory found: \033[1;32m" + request.url + "\033[m", "info")
                foundRoutes.append(str(route).replace("\n", ""))

    except KeyboardInterrupt:
        message("")
        message("Exiting... Goodbye", "error")
        message("Finished with " + str(len(foundRoutes)) + " results!", "finished")
        exit()
    except requests.exceptions.ConnectionError:
        message("Service not found", "error")
        exit()

    message("Finished with " + str(len(foundRoutes)) + " results!", "finished")


start()
if __name__ == "__main__":
    if args.url and args.wordlist:
        Thread(target=search(args.url, args.wordlist)).start()
    elif args.url and not args.wordlist:
        wordlist = "/usr/share/dirb/wordlists/common.txt"
        Thread(target=search(args.url, wordlist)).start()
