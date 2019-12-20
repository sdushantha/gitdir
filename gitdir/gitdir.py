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
    From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
    """

    # extract the branch name from the given url (e.g master)
    branch = re.findall(r"/tree/(.*?)/", url)
    api_url = url.replace("https://github.com", "https://api.github.com/repos")
    if len(branch) == 0:
        branch = re.findall(r"/blob/(.*?)/", url)[0]
        download_dirs = re.findall(r"/blob/" + branch + r"/(.*)", url)[0]
        api_url = re.sub(r"/blob/.*?/", "/contents/", api_url)
    else:
        branch = branch[0]
        download_dirs = re.findall(r"/tree/" + branch + r"/(.*)", url)[0]
        api_url = re.sub(r"/tree/.*?/", "/contents/", api_url)

    api_url = api_url + "?ref=" + branch
    return api_url, download_dirs


def download(repo_url, flatten=False, output_dir="./"):
    """ Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
     sub-directories will be pulled upwards into the root folder. """

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    # To handle file names.
    if not flatten:
        if len(download_dirs.split(".")) == 0:
            dir_out = os.path.join(output_dir, download_dirs)
        else:
            dir_out = os.path.join(output_dir, "/".join(download_dirs.split("/")[0:-1]))
    else:
        dir_out = output_dir

    try:
        response = urllib.request.urlretrieve(api_url)
    except KeyboardInterrupt:
        # when CTRL+C is pressed during the execution of this script,
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print_text("✘ Got interrupted", "red", in_place=True)
        exit()

    if not flatten:
        # make a directory with the name which is taken from
        # the actual repo
        os.makedirs(dir_out, exist_ok=True)

    # total files count
    total_files = 0

    with open(response[0], "r") as f:
        raw_data = f.read()

        data = json.loads(raw_data)
        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        # If the data is a file, download it as one.
        if isinstance(data, dict) and data["type"] == "file":
            try:
                # download the file
                urllib.request.urlretrieve(data["download_url"], os.path.join(dir_out, data["name"]))
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print_text("Downloaded: " + Fore.WHITE + "{}".format(data["name"]), "green", in_place=True)

                return total_files
            except KeyboardInterrupt:
                # when CTRL+C is pressed during the execution of this script,
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print_text("✘ Got interrupted", 'red', in_place=False)
                exit()

        for index, file in enumerate(data):
            file_url = file["download_url"]
            file_name = file["name"]

            if flatten:
                path = os.path.basename(file["path"])
            else:
                path = file["path"]

            path = os.path.join(dir_out, path)
            if file_url is not None:
                try:
                    # download the file
                    urllib.request.urlretrieve(file_url, path)

                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("Downloaded: " + Fore.WHITE + "{}".format(file_name), "green", in_place=True,
                               flush=True)

                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("✘ Got interrupted", 'red', in_place=False)
                    exit()
            else:
                download(file["html_url"], flatten, path)

    return total_files


def main():
    if sys.platform != 'win32':
        # disbale CTRL+Z
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    parser = argparse.ArgumentParser(description="Download directories/folders from GitHub")
    parser.add_argument('urls', nargs="+",
                        help="List of Github directories to download.")
    parser.add_argument('--output_dir', "-d", dest="output_dir", default="./",
                        help="All directories will be downloaded to the specified directory.")

    parser.add_argument('--flatten', '-f', action="store_true",
                        help='Flatten directory structures. Do not create extra directory and download found files to'
                             ' current directory.')

    args = parser.parse_args()

    flatten = args.flatten
    for url in args.urls:
        total_files = download(url, flatten, args.output_dir)

    print_text("✔ Download complete", "green", in_place=True)


if __name__ == "__main__":
    main()
