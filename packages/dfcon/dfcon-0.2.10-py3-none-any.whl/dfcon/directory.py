"""Directory instance for database collector"""

from __future__ import annotations

import os
import re
import shutil
from typing import Any, Callable, List, Optional, Union, Generator

from cmpfilter import Filter, EmpFilter


class Directory:
    """This class is used to represent a directory in the database."""

    def __init__(
        self,
        path: Optional[str] = None,
    ) -> None:
        if path is None:
            return
        if path == "":
            raise ValueError("'path' must not be empty. If you want to use the current directory, use '.' or './'.")

        self.name = ""
        self.path = ""
        self.abspath = ""

        self.set_params(path)

    def set_params(self, path: str) -> Directory:
        if not os.path.isdir(path):
            raise ValueError(f"'{path}' is not a directory.")
        path = path.rstrip("\\/ ")

        path = os.sep.join(re.split(r"[\\/]", path))
        name = path.rsplit(os.sep, maxsplit=1)[-1]

        self.name = name
        self.path = path
        self.abspath = os.path.abspath(path)

        return self

    def __str__(self) -> str:
        return self.path

    def __eq__(self, __value: Union[str, Directory]) -> bool:
        if not isinstance(__value, (str, Directory)):
            raise TypeError(f"'{type(__value).__name__}' object is not allowed for comparison.")
        return os.path.abspath(self.path) == os.path.abspath(str(__value))

    def check_form_filter(self, filters: Optional[Union[Filter, List[Filter]]] = None) -> Filter:
        if filters is None:
            filters = EmpFilter()
        elif isinstance(filters, list) and isinstance(filters[0], Filter):
            filters = Filter.overlap(filters)
        elif isinstance(filters, Filter):
            pass
        else:
            raise TypeError(f"'{type(filters).__name__}' object is not allowed for comparison.")
        return filters

    def get_file_path(self, filters: Optional[Union[Filter, List[Filter]]] = None) -> Generator[str, None, None]:
        """Get the path of the file in the directory.

        Args:
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for file path. Defaults to None.

        Returns:
            Generator[str, None, None]: file path generator
        """
        filters = self.check_form_filter(filters)

        for cur_dir, _, files in os.walk(self.path):
            for f in files:
                fpath = os.path.join(cur_dir, f)
                if filters(fpath):
                    yield fpath

    def get_terminal_instances(
        self, filters: Optional[Union[Filter, List[Filter]]] = None, return_generator: bool = False
    ) -> Union[List[Directory], Generator[Directory, None, None]]:
        """Get the terminal directory instances in the directory.

        Args:
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for directory path. Defaults to None.

        Returns:
            List[Directory]: directory instance list
        """
        return self.get_instances(filters, terminal_only=True, child_only=False, return_generator=return_generator)

    def get_child_instances(
            self, filters: Optional[Union[Filter, List[Filter]]] = None, return_generator: bool = False
        ) -> Union[List[Directory], Generator[Directory, None, None]]:
        """Get the child directory instances in the directory.

        Args:
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for directory path. Defaults to None.

        Returns:
            List[Directory]: directory instance list
        """
        return self.get_instances(filters, terminal_only=False, child_only=True, return_generator=return_generator)

    def get_instances(
        self,
        filters: Optional[Union[Filter, List[Filter]]] = None,
        terminal_only: bool = False,
        child_only: bool = False,
        return_generator: bool = False
    ) -> Union[List[Directory], Generator[Directory, None, None]]:
        """Get the directory instances in the directory.

        Args:
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for directory path. Defaults to None.

        Returns:
            List[Directory]: directory instance list
        """
        filters = self.check_form_filter(filters)

        dir_path = []
        for cur_dir, dirs, _ in os.walk(self.path):
            if terminal_only and dirs != []:
                continue
            if child_only and os.path.abspath(cur_dir) != os.path.abspath(self.path):
                continue
            dir_path.append(cur_dir)

        if return_generator:
            yield from (Directory(path) for path in dir_path if filters(path))
        else:
            return [Directory(path) for path in dir_path if filters(path)]

    def get_abspath(self) -> str:
        """get absolute path which is sep by '/'"""
        return "/".join(self.abspath.split(os.sep))

    def incarnate(
        self,
        path: str,
        name: Optional[str] = None,
        filters: Optional[Union[Filter, List[Filter]]] = None,
        printer: Optional[Callable[[str], Any]] = None,
        empty: bool = False,
    ) -> Directory:
        """incarnate directory instance

        Args:
            path (str): path of directory
            name (Optional[str], optional): name of directory. Defaults to None.
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for directory path. Defaults to None.
            printer (Optional[Callable[[str], Any]], optional): log-printer function. Defaults to None.
            empty (bool, optional): If True, the directory will be empty. Defaults to False.

        Returns:
            Directory: directory instance
        """

        def transformer(old_path: str) -> str:
            if not os.path.isabs(old_path):
                old_path = os.path.abspath(old_path)
            new_path = old_path.replace(self.abspath, path)
            return new_path

        filters = self.check_form_filter(filters)

        if printer is None:
            printer = lambda _: None
        path = os.sep.join(path.split("/"))
        if name is not None:
            path = os.path.join(path, name)
        else:
            path = os.path.join(path, self.name)
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.isdir(path):
            os.mkdir(path)

        printer(f"incarnate: {path}")
        for cur_dir, dirs, files in os.walk(self.path):
            for d in dirs:
                dpath = os.path.join(cur_dir, d)
                new_path = transformer(dpath)
                if os.path.exists(new_path):
                    printer(f"skip: {new_path}")
                    continue
                printer(f"mkdir: {new_path}")
                os.mkdir(new_path)
            for f in files:
                fpath = os.path.join(cur_dir, f)
                new_path = transformer(fpath)
                if filters(fpath) and not empty:
                    if os.path.exists(new_path):
                        printer(f"skip: {new_path}")
                        continue
                    printer(f"copy: {new_path}")
                    shutil.copy(fpath, new_path)

        return Directory(os.path.relpath(path))

    def remove_member(
        self,
        filters: Optional[Union[Filter, List[Filter]]] = None,
        printer: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Remove member of directory

        Args:
            filters (Optional[Union[Filter, List[Filter]]], optional): Filter for path. Defaults to None.
            printer (Optional[Callable[[str], Any]], optional): printer function. Defaults to None.
        """

        filters = self.check_form_filter(filters)

        if printer is None:
            printer = lambda _: None

        remove_files = self.get_file_path(filters=filters)
        for file in remove_files:
            printer(f"remove: {file}")
            os.remove(file)

        return
