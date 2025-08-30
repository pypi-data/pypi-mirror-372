"""Database file path collector"""

import os
import shutil

# import sys
# sys.path.append("../")
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dfcon.directory import Directory
from dfcon.path_filter import FileFilter, DircFilter, Filter


if __name__ == "__main__":
    if os.path.exists("test/out/exp1/ABCD"):
        shutil.rmtree("test/out/exp1/ABCD")
    if os.path.exists("test/out/out"):
        shutil.rmtree("test/out/out")
    os.mkdir("test/out/out")

    dirc = Directory(path="test/out/exp1")

    print("################# EX1 #################\n")

    # example1
    file_filter = FileFilter().include_extention(["py", "txt"])
    dirc_filter = DircFilter().uncontained_path(["log", "data", ".git"])
    filters = Filter.overlap([file_filter, dirc_filter])

    results = dirc.get_file_path(filters=filters)
    all_dir_instances = dirc.get_instances(filters=None)
    terminal_dirs = dirc.get_terminal_instances(filters=None)

    for r in all_dir_instances:
        print(f"collect dirs: {r}")
    print()

    for r in terminal_dirs:
        print(f"collect term: {r}")
    print()

    for r in results:
        print(f"collect path: {r}")
    print()

    print("\n################# EX2 #################\n")

    # example2
    dirc.incarnate(path="test/out/out", name="res", filters=filters)
    dirc.incarnate(path="test/out/out", name="res2", filters=filters, empty=True)
