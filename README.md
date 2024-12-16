## Installation

```console
#clone the repo
$ git clone https://github.com/vinnyrobot/robotBuster.git
$ cd robotBuster

#install the requirements
$ python3 -m pip install -r requirements.txt
```


## Running as root

```console
$ sudo mv robotBuster.py robotBuster
$ sudo cp robotBuster /bin
$ cd
$ cd /bin
$ sudo chmod +x robotBuster
```

## Usage

```console
$ robotBuster --help
usage: robotBuster [-h] -u URL [-w WORDLIST] [-v]

Directory searcher

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     specify a target url
  -w WORDLIST, --wordlist WORDLIST
                        specifies a wordlist to search.
  -v, --version         show tool version and exit.
```
