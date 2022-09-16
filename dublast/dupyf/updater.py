"""Checks for updates for RxOT tools"""

from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen
from json import loads
import platform
import ssl

def checkUpdate(url, toolName, version, host, hostVersion, preRelease = False, language = "en"):
    """Checks if an update is available"""

    # Check os
    os  = platform.system()
    if os == "Windows":
        os = "win"
    elif os == "Darwin":
        os = "mac"
    elif os == "Linux":
        os = "linux"

    args = {
        "getVersion": "",
        "name": toolName,
        "version": version,
        "os": os,
        "osVersion": platform.version(),
        "host": host,
        "hostVersion": hostVersion,
        "languageCode": language,
    }

    if preRelease:
        args["preRelease"] = ""

    response = request(url, args, False)
    return loads(response.read())

def request(url, args=None, secured=True):
    """Builds a GET request with the args"""

    response = ""

    if args:
        first = True
        for arg in args:
            if first:
                url = url + '?'
                first = False
            else:
                url = url + '&'
            url = url + arg
            val = args[arg]
            if val != "":
                url = url + '=' + quote(val, safe='')
    try:
        response = urlopen(url)
    except URLError:
        if not secured:
            sslContext = ssl._create_unverified_context()
            response = urlopen(url, context=sslContext)

    return response

if __name__ == "__main__":
    data = checkUpdate('https://api.rxlab.io', "Ramses-Maya", "0.5.0", "Maya", "2023")
    print(data)
