from sys import argv

from pygmail.types import Account

if __name__ == "__main__":
    account = Account(argv[1])
