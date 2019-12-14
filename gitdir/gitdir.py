#!/usr/bin/python3
import re
import os
import urllib.request
import signal
import argparse
import json
import sys
from colorama import Fore, Style, init

init()

# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"

COLOR_NAME_TO_CODE = {"default": "", "red": Fore.RED, "green": Style.BRIGHT + Fore.GREEN}


def print_text(text, color="default", in_place=False, **kwargs):  # type: (str, str, bool, any) -> None
    """
    print text to console, a wrapper to built-in print

    :param text: text to print
    :param color: can be one of "red" or "green", or "default"
    :param in_place: whether to erase previous line and print in place
    :param kwargs: other keywords passed to built-in print
    """
    if in_place:
        print("\r" + ERASE_LINE, end="")
    print(COLOR_NAME_TO_CODE[color] + text + Style.RESET_ALL, **kwargs)


def create_url(url):
    """
    modifying the given url so that it returns JSON data when
    we do a GET requests later in this script
    """

    # extract the branch name from the given url (e.g master)
    branch = re.findall(r"/tree/(.*?)/", url)[0]

    # extract the dirs name from the given url (e.g master)
    download_dirs = re.findall(r"/tree/" + branch + r"/(.*)", url)[0]

    api_url = url.replace("https://github.com", "https://api.github.com/repos")
    api_url = re.sub(r"/tree/.*?/", "/contents/", api_url)

    api_url = api_url + "?ref=" + branch

    return (api_url, download_dirs)


def download(repo_url, flatten):
    '''
    recursive download
    '''

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    try:
        r = urllib.request.urlretrieve(api_url)

    except KeyboardInterrupt:
        # when CTRL+C is pressed during the execution of this script,
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print_text("✘ Got interrupted", "red", in_place=True)
        exit()

    if not flatten:
        # make a directory with the name which is taken from
        # the actual repo
        os.makedirs(download_dirs, exist_ok=True)

    # total files count
    total_files = 0

    with open(r[0], "r") as f:
        raw_data = f.read()

        data = json.loads(raw_data)

        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        for index, file in enumerate(data):
            file_url = file["download_url"]
            fname = file["name"]

            if flatten:
                path = os.path.basename(file["path"])
            else:
                path = file["path"]

            if not file_url is None:
                try:
                    # download the file
                    urllib.request.urlretrieve(file_url, path)

                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("Downloaded: " + Fore.WHITE + "{}".format(fname), "green", in_place=True, end="",
                               flush=True)

                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("✘ Got interrupted", 'red', in_place=True)
                    exit()
            else:
                download(file["html_url"], flatten)

    return total_files


def main():
    if sys.platform != 'win32':
        # disbale CTRL+Z
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    parser = argparse.ArgumentParser(description="Download directories/folders from GitHub")
    parser.add_argument('url', action="store")

    parser.add_argument('--flatten', '-f', action="store_true", help='Flatten directory structures. Do not create extra'
                                                                     ' directory and download found files to current'
                                                                     ' directory.')

    args = parser.parse_args()

    repo_url = args.url
    flatten = args.flatten

    total_files = download(repo_url, flatten)

    print_text("✔ Download complete", "green", in_place=True)


if __name__ == "__main__":
    main()
