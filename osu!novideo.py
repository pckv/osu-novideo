""" When running:
    Remove all videos of *.avi extension recursively from a directory. (osu!/Songs/) """

from os import scandir, remove, stat
from os import path as _path
from argparse import ArgumentParser
from functools import partial
from datetime import datetime
import typing


__version__ = "0.3"


def valid_path(path: str):
    """ Checks if given path is a valid folder """
    if _path.exists(path):
        if _path.isdir(path):
            return path

    return False


def to_gb(size: int):
    """ Convert size to formatted float representing Gigabytes.
    size should be an int of bytes."""
    return round(size / 1024**3, 3)


def confirm(prompt: str, end: str=" [Y/n] "):
    """ Confirm a task, prompting a string and parsing Y/n """
    user_input = input(str(prompt) + str(end))

    return user_input.lower() == "y"


def output_log(text: str, handler: typing.io):
    """ Print to stdout and write to a stream. """
    print(text, file=handler)
    print(text)


def remove_files(path: str, ext: str):
    """ Go through all folders and remove any *.ext in the folder
    (not further recursively) """
    count, size_removed = 0, 0

    # Create a log handler and define a function for writing to file
    log_handler = open("osu!novideo.log", "a")
    log = partial(output_log, handler=log_handler)

    # Log the time the command started
    log("Started {0}; removing *.{ext} from \"{path}\"".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path=path, ext=ext))

    for entry in scandir(path):
        # We want to delete the file *in* a directory
        if not entry.is_dir():
            continue

        # Go through the found folder and remove every file ending with ext
        for file in scandir(entry.path):
            if not file.is_file():
                continue

            if file.name.endswith("." + ext):
                count += 1
                size_removed += stat(file.path).st_size

                # Print when removing file
                try:
                    log("Removing file \"{0.name}\"".format(file))
                except UnicodeEncodeError:
                    try:
                        log("Removing unreadable file in folder \"{0.name}\"".format(entry))
                    except UnicodeEncodeError:
                        log("Removing some file, at least (folder and name is not readable)")

                # Remove the file (there's no turning back!)
                try:
                    remove(file.path)
                except PermissionError:
                    log("No permission to remove files. Perhaps you're not running as admin?")
                    return

    log("Removed {0} files of size {1}GB".format(count, to_gb(size_removed)))
    log_handler.close()


def main():
    """ Parse arguments:
        --path PATH -p PATH     path where default is current directory
        --ext EXT -e EXT        extension where default is avi

    Afterwards deletes all found files with given extension"""
    parser = ArgumentParser(description="Remove useless videos from osu!/Songs/")
    parser.add_argument("--path", "-p", help="Your osu!/Songs/ folder path.", metavar="PATH", default="./",
                        type=valid_path)
    parser.add_argument("--ext", "-e", help="File extension to remove.", metavar="EXT", default="avi", type=str)
    parser.add_argument("--version", "-V", help="Display the script's version.", action="version",
                        version="%(prog)s {}".format(__version__))
    args = parser.parse_args()

    # Exit when the path is invalid
    if not args.path:
        print("The given path is invalid.")
        return False

    path = _path.abspath(args.path)

    if confirm("Are you sure you want to remove all .{ext} from\n\"{dir}\"?".format(ext=args.ext, dir=path)):
        remove_files(args.path, ext=args.ext)
    else:
        print("Task aborted.")


if __name__ == "__main__":
    main()
