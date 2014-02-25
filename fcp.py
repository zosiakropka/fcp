from optparse import OptionParser
import re
from re import LOCALE, UNICODE
#import ftplib
import pprint

# @todo home directory
PATH_PATTERN = "([^\0]+\/?)*"
PATH_BEGINNING_PATTERN = "~?\/"
PATH_FULL_PATTERN = "(%s)(%s)" % (PATH_BEGINNING_PATTERN, PATH_PATTERN)
USER_PATTERN = "\w+"
IP_PATTERN = "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
HOSTNAME_PATTERN = "[a-zA-Z\d\-\.]+"
HOST_PATTERN = "(%s)|(%s)" % (IP_PATTERN, HOSTNAME_PATTERN)
REMOTE_PATTERN = "^(%s@)?(%s)\:(%s)$" % (USER_PATTERN, HOST_PATTERN, PATH_FULL_PATTERN)
REMOTE_USER_PATTERN = "^(%s)@(%s)\:(%s)$" % (USER_PATTERN, HOST_PATTERN, PATH_FULL_PATTERN)
REMOTE_ANONYM_PATTERN = "^(%s)\:(%s)$" % (HOST_PATTERN, PATH_FULL_PATTERN)
LOCAL_PATTERN = "^(%s)?(%s)$" % (PATH_BEGINNING_PATTERN, PATH_PATTERN)
FTP_PORT = 21


def fcp(source, destination, port=FTP_PORT, password=None):
    remote_re = re.compile(REMOTE_PATTERN, flags=(UNICODE | LOCALE))
    remote_user_re = re.compile(REMOTE_USER_PATTERN, flags=(UNICODE | LOCALE))
    remote_anonym_re = re.compile(REMOTE_ANONYM_PATTERN, flags=(UNICODE | LOCALE))
    local_re = re.compile(LOCAL_PATTERN, flags=(UNICODE | LOCALE))

    files = {
        "source": {
            "string": source
        },
        "destination": {
            "string": destination
        }
    }

    for f in files.itervalues():
        string = f["string"]
        if remote_re.match(string):
            f["remote"] = True
            path_start = re.search("(%s)$" % (PATH_FULL_PATTERN), string).start()
            f["path"] = string[path_start:len(string)]
            if remote_user_re.match(string):
                username_end = re.search("^(%s)@" % (USER_PATTERN), string).end() - 1
                f["username"] = string[0:username_end]
                host_start = username_end + 1
            elif remote_anonym_re.match(string):
                f["username"] = None
                host_start = 0
            else:
                raise Exception("Wrong param")
            host_end = path_start - 1
            f["host"] = string[host_start:host_end]
        elif local_re.match(string):
            f["remote"] = False
            f["path"] = string
        else:
            raise Exception("Wrong param")

    pprint.pprint(files)

    # between remotes
    if files["source"]["remote"] and files["destination"]["remote"]:
        raise Exception("Copy between two remotes not implemented.")

    # between locals
    if not files["source"]["remote"] and not files["destination"]["remote"]:
        raise Exception("Copy between two locals not implemented.")

    # remote to local
    if files["source"]["remote"] and not files["destination"]["remote"]:
        raise Exception("Copy from remote to local not implemented.")

    # local to remote
    if not files["source"]["remote"] and not files["destination"]["remote"]:
        raise Exception("Copy from local to remote not implemented.")


def main():
    usage = "usage: %prog [options] [USER@HOST:]SOURCE [USER@HOST:]DESTINATION"
    parser = OptionParser(usage)
    parser.add_option("-P", "--port", dest="port", default=FTP_PORT,
                      help="Specifies the port to connect to on the remote "\
                      "host. Note that this option is written with a "\
                      "capital P")
    parser.add_option("-r", dest="recursive",
                      help="Recursively copy entire directories.")
    parser.add_option("-p", "--password", dest="password",
                      help="Password")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")

    source = args[0]
    destination = args[1]

    port = options.port
    password = options.password

    fcp(source=source, destination=destination, port=port, password=password)

if __name__ == "__main__":
    main()
