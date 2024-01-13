#!/usr/bin/python3
import re
import os
import urllib.request
import signal
import argparse
import json
import sys
from colorama import Fore, Style, init
from pathlib import Path

init()

# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"

COLOR_NAME_TO_CODE = {
    "default": "",
    "red": Fore.RED,
    "green": Style.BRIGHT + Fore.GREEN,
    "yellow": Style.BRIGHT + Fore.YELLOW,
}


class FileToDownload:
    def __init__(self, name, url, path, dest_path):
        self.name = name
        self.url = url
        self.path = path
        self.dest_path: Path = dest_path


def print_text(text, color="default", in_place=False, **kwargs) -> None:
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


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """
    Prompt user for a yes/no question.

    :param question: question to ask
    :param default: default answer if user just presses enter
    :return: True if user answers yes, False if user answers no
    """
    if default:
        yes_no = "Y/n"
    else:
        yes_no = "y/N"

    while True:
        print_text("{} [{}] ".format(question, yes_no), end="")
        choice = input().lower()
        if choice in {"y", "yes"}:
            return True
        elif choice in {"n", "no"}:
            return False
        elif choice == "":
            return default
        else:
            print_text("Please respond with 'yes' or 'no' (or 'y' or 'n').")


def create_url(url):
    """
    From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
    """
    repo_only_url = re.compile(
        r"https:\/\/github\.com\/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}\/[a-zA-Z0-9]+$"
    )
    re_branch = re.compile("/(tree|blob)/(.+?)/")

    # Check if the given url is a url to a GitHub repo. If it is, tell the
    # user to use 'git clone' to download it
    if re.match(repo_only_url, url):
        print_text(
            "✘ The given url is a complete repository. Use 'git clone' to download the repository",
            "red",
            in_place=True,
        )
        sys.exit()

    # extract the branch name from the given url (e.g master)
    branch = re_branch.search(url)
    if branch is None:
        print_text(
            "✘ Could not find branch name in the given url", "red", in_place=True
        )
        sys.exit()
    download_dirs = url[branch.end() :]
    api_url = (
        url[: branch.start()].replace("github.com", "api.github.com/repos", 1)
        + "/contents/"
        + download_dirs
        + "?ref="
        + branch.group(2)
    )
    return api_url, download_dirs


def download_file(file_to_download: FileToDownload, force: bool) -> None:
    if os.path.exists(file_to_download.dest_path) and not force:
        if prompt_yes_no(
            "✘ File {} already exists. Overwrite?".format(file_to_download.dest_path),
            default=False,
        ):
            urllib.request.urlretrieve(file_to_download.url, file_to_download.dest_path)
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            print_text(
                "Downloading (overwriting): "
                + Fore.WHITE
                + "{} to {}".format(
                    file_to_download.name, file_to_download.dest_path.resolve()
                ),
                "green",
                in_place=True,
            )
        else:
            print_text(
                "Skipped: " + Fore.WHITE + "{}".format(file_to_download.name),
                "yellow",
                in_place=True,
            )
    else:
        urllib.request.urlretrieve(file_to_download.url, file_to_download.dest_path)
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print_text(
            "Downloaded: "
            + Fore.WHITE
            + "{} to {}".format(file_to_download.name, file_to_download.dest_path),
            "green",
            in_place=True,
        )


def download(repo_url, flatten=False, force=False, output_dir="./"):
    """Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
    sub-directories will be pulled upwards into the root folder."""

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    # To handle file names.
    if not flatten:
        if len(download_dirs.split(".")) == 0:
            dir_out = os.path.join(output_dir, download_dirs)
        else:
            dir_out = os.path.join(output_dir, "/".join(download_dirs.split("/")[:-1]))
    else:
        dir_out = output_dir

    dir_out = Path(dir_out)

    try:
        response = urllib.request.urlretrieve(api_url)
    except KeyboardInterrupt:
        # when CTRL+C is pressed during the execution of this script,
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print_text("✘ Got interrupted", "red", in_place=True)
        sys.exit()

    if not flatten:
        # make a directory with the name which is taken from the actual repo
        os.makedirs(dir_out, exist_ok=True)

    # total files count
    total_files = 0

    with open(response[0], "r") as f:
        data = json.load(f)
        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        # If the data is a file, download it as one.
        if isinstance(data, dict) and data["type"] == "file":
            print("Single file download")
            try:
                # download the file
                dest_path = dir_out / Path(data["name"])
                file_to_download = FileToDownload(
                    name=data["name"],
                    url=data["download_url"],
                    dest_path=dest_path,
                    path=data["path"],
                )
                download_file(file_to_download, force)

                return total_files
            except KeyboardInterrupt:
                # when CTRL+C is pressed during the execution of this script,
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print_text("✘ Got interrupted", "red", in_place=False)
                sys.exit()

        for file in data:
            file_path = file["path"]

            if flatten:
                path = Path(os.path.basename(file_path))
            else:
                path = Path(file_path)

            file_to_download = FileToDownload(
                name=file["name"],
                url=file["download_url"],
                dest_path=path,
                path=file["path"],
            )

            if path.parent != "":
                os.makedirs(path.parent, exist_ok=True)
            else:
                pass

            if file_to_download.url is not None:
                try:
                    download_file(file_to_download, force)
                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("✘ Got interrupted", "red", in_place=False)
                    sys.exit()
            else:
                download(file["html_url"], flatten, force, download_dirs)

    return total_files


def set_up_url_opener():
    """
    Set up the URL opener to mimic a browser.
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)


def main():
    if sys.platform != "win32":
        # disbale CTRL+Z
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    parser = argparse.ArgumentParser(
        description="Download directories/folders from GitHub"
    )
    parser.add_argument(
        "urls", nargs="+", help="List of Github directories to download."
    )
    parser.add_argument(
        "--output_dir",
        "-d",
        dest="output_dir",
        default="./",
        help="All directories will be downloaded to the specified directory.",
    )

    parser.add_argument(
        "--flatten",
        "-f",
        action="store_true",
        help="Flatten directory structures. Do not create extra directory and download found files to"
        " output directory. (default to current directory if not specified)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwriting existing files.",
    )

    args = parser.parse_args()

    set_up_url_opener()

    flatten = args.flatten
    for url in args.urls:
        download(url, flatten, args.force, args.output_dir)

    print_text("✔ Download complete", "green", in_place=True)


if __name__ == "__main__":
    main()
