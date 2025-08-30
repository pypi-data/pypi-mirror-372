"""Filter subclasses for dataFileController (DFCon)"""

from __future__ import annotations
import os
import re
from typing import List

from cmpfilter import Filter

from .directory import Directory


class FileFilter(Filter):
    """Filter subclass for file filtering"""

    def __init__(self) -> None:
        self._contain_literal = []
        self._exclude_literal = []
        self._extention = []
        self._ex_extention = []
        self._start_with = []
        self._end_with = []

    def __call__(self, target: str) -> bool:
        if isinstance(target, Directory):
            return True
        if not isinstance(target, str):
            raise TypeError(
                "The argument 'target' type must be 'str', " + f" but detect '{target.__class__.__name__}'",
            )

        target = os.sep.join(re.split(r"[\\/]", target))

        if os.path.isdir(target):
            return True
        if not os.path.exists(target):
            raise ValueError(f"{target} dose not exist.")

        if self._extention:
            ext = os.path.splitext(target)[-1][1:]
            if not ext in self._extention:
                return False

        if self._ex_extention:
            ext = os.path.splitext(target)[-1][1:]
            if ext in self._ex_extention:
                return False

        if self._contain_literal:
            exist = False
            for literal in self._contain_literal:
                if literal in os.path.basename(target):
                    exist = True
                    break
            if not exist:
                return False

        if self._exclude_literal:
            for literal in self._exclude_literal:
                if literal in os.path.basename(target):
                    return False

        if self._start_with:
            exist = False
            for literal in self._start_with:
                if os.path.basename(target).startswith(literal):
                    exist = True
                    break
            if not exist:
                return False

        if self._end_with:
            exist = False
            for literal in self._end_with:
                ext = os.path.splitext(target)[-1]
                if os.path.basename(target).endswith(literal + ext):
                    exist = True
                    break
            if not exist:
                return False

        return True

    def chake_form_args(self, literal: List[str] | str) -> List[str]:
        """Check the type of the argument.

        Args:
            literal (List[str] | str): The argument to check.

        Raises:
            TypeError: If the argument is not a string or a list of strings.
        """

        if isinstance(literal, str):
            return [literal]
        elif not isinstance(literal, list):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        elif literal == []:
            return literal
        elif not isinstance(literal[0], str):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        else:
            return literal

    def contained(self, literal: List[str] | str) -> FileFilter:
        """set criteria, get file name which contain `literal`.
        The criteria behaves like the logical sum.

        Args:
            literal (List[str] | str): Criteria for filtering files
            that contain `literal` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        literal = self.chake_form_args(literal)

        self._contain_literal += literal

        return self

    def uncontained(self, literal: List[str] | str) -> FileFilter:
        """set criteria, get file name which dose not contain `literal`.
        This criteria behaves like the negative logical sum.

        Args:
            literal (List[str] | str): Criteria for filtering files
            that dose not contain `literal` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        literal = self.chake_form_args(literal)

        self._exclude_literal += literal

        return self

    def include_extention(self, extention: List[str] | str) -> FileFilter:
        """Specify the including file extension.
        The criteria behaves like the logical sum.

        Args:
            extention (List[str] | str): Criteria for filtering files
            that dose not contain `extention` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        extention = self.chake_form_args(extention)

        self._extention += extention

        return self

    def exclude_extention(self, extention: List[str] | str) -> FileFilter:
        """Specify the excluding file extension.
        This criteria behaves like the negative logical sum.

        Args:
            extention (List[str] | str): Criteria for filtering files
            that dose not contain `extention` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        extention = self.chake_form_args(extention)

        self._ex_extention += extention

        return self

    def start_with(self, literal: List[str] | str) -> FileFilter:
        """set criteria, get file name which start with `literal`.
        The criteria behaves like the logical sum.

        Args:
            literal (List[str] | str): Criteria for filtering files
            that start with `literal` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        literal = self.chake_form_args(literal)

        self._start_with += literal

        return self

    def end_with(self, literal: List[str] | str) -> FileFilter:
        """set criteria, get file name which end with `literal`.
        This criteria behaves like the negative logical sum.

        Args:
            literal (List[str] | str): Criteria for filtering files
            that end with `literal` in the filename.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        literal = self.chake_form_args(literal)

        self._end_with += literal

        return self

    def __str__(self) -> str:
        cond_str = "FileFilter\n"
        for key, value in vars(self).items():
            if value:
                cond_str += " - " + key + " : [" + ",".join(value) + "]\n"

        return cond_str


class DircFilter(Filter):
    """Filter subclass for  directory filtering"""

    def __init__(self) -> None:
        self._only_terminal_dirc = False
        self._contain_dirc = []
        self._exclude_dirc = []
        self._contain_literal = []
        self._exclude_literal = []

    def __call__(self, target: str | Directory) -> bool:
        if isinstance(target, Directory):
            target = target.path
        elif not isinstance(target, str):
            raise TypeError(f"The argument 'target' type must be 'str', but detect '{target.__class__.__name__}'")
        if isinstance(target, str):
            if os.path.isfile(target):
                target = os.path.dirname(target)
        if os.path.isfile(target):
            target = os.path.dirname(target)

        target = os.sep.join(re.split(r"[\\/]", target))

        if self._only_terminal_dirc:
            mems = os.listdir(target)
            for mem in mems:
                if os.path.isdir(os.path.join(target, mem)):
                    return False

        if self._contain_dirc:
            dircs = target.split(os.sep)
            exist = False
            for target_dirc in self._contain_dirc:
                if target_dirc in dircs:
                    exist = True
                    break
            if not exist:
                return False

        if self._exclude_dirc:
            dircs = target.split(os.sep)
            for target_dirc in self._exclude_dirc:
                if target_dirc in dircs:
                    return False

        if self._contain_literal:
            dircs = target.split(os.sep)
            exist = False
            for target_literal in self._contain_literal:
                for dirc in dircs:
                    if target_literal in dirc:
                        exist = True
                        break
            if not exist:
                return False

        if self._exclude_literal:
            dircs = target.split(os.sep)
            for target_literal in self._exclude_literal:
                for dirc in dircs:
                    if target_literal in dirc:
                        return False

        return True

    def only_terminal(self, set_status: bool = True) -> DircFilter:
        """set criteria, get file path only terminal directory files

        Args:
            set_status (bool): When `set_status=True`, get only terminal directory.

        Returns:
            DircFilter: Callable instance that filters by specified criteria.
        """
        self._only_terminal_dirc = set_status

        return self

    def contained_path(self, dirc_name: List[str] | str) -> DircFilter:
        """Set criteria, get file path which contain `dirc_name`.
        This criteria behaves like the logical sum.

        Args:
            dirc_name (List[str] | str):
                Criteria for filtering directory
                that contain `dirc_name` in the path.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        if isinstance(dirc_name, str):
            dirc_name = [dirc_name]
        elif not isinstance(dirc_name, list):
            raise TypeError(
                "The argument 'dirc_name' type must be 'str' or 'List[str]', "
                + f"but detect '{dirc_name.__class__.__name__}'",
            )
        elif dirc_name == []:
            return self
        elif not isinstance(dirc_name[0], str):
            raise TypeError(
                "The argument 'dirc_name' type must be 'str' or 'List[str]', "
                + f"but detect '{dirc_name.__class__.__name__}'",
            )
        self._contain_dirc += dirc_name

        return self

    def uncontained_path(self, dirc_name: List[str] | str) -> DircFilter:
        """Set criteria, get file path which dose not contain `dirc_name`.
        This criteria behaves like the negative logical sum.

        Args:
            dirc_name (List[str] | str):
                Criteria for filtering directory
                that dose not contain `dirc_name` in the path.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        if isinstance(dirc_name, str):
            dirc_name = [dirc_name]
        elif not isinstance(dirc_name, list):
            raise TypeError(
                "The argument 'dirc_name' type must be 'str' or 'List[str]', "
                + f"but detect '{dirc_name.__class__.__name__}'",
            )
        elif dirc_name == []:
            return self
        elif not isinstance(dirc_name[0], str):
            raise TypeError(
                "The argument 'dirc_name' type must be 'str' or 'List[str]', "
                + f"but detect '{dirc_name.__class__.__name__}'",
            )
        self._exclude_dirc += dirc_name

        return self

    def contained_literal(self, literal: List[str] | str) -> DircFilter:
        """Set criteria, get file path which contain `literal`.
        This criteria behaves like the logical sum.

        Args:
            literal (List[str] | str):
                Criteria for filtering directory
                that contain `literal` in the directory name.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        if isinstance(literal, str):
            literal = [literal]
        elif not isinstance(literal, list):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        elif literal == []:
            return self
        elif not isinstance(literal[0], str):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        self._contain_literal += literal

        return self

    def uncontained_literal(self, literal: List[str] | str) -> DircFilter:
        """Set criteria, get file path which contain `literal`.
        This criteria behaves like the negative logical sum.

        Args:
            literal (List[str] | str):
                Criteria for filtering directory
                that uncontain `literal` in the directory name.

        Returns:
            FileFilter: Callable instance that filters by specified criteria.
        """

        if isinstance(literal, str):
            literal = [literal]
        elif not isinstance(literal, list):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        elif literal == []:
            return self
        elif not isinstance(literal[0], str):
            raise TypeError(
                "The argument 'literal' type must be 'str' or 'List[str]', "
                + f"but detect '{literal.__class__.__name__}'",
            )
        self._exclude_literal += literal

        return self

    def __str__(self) -> str:
        cond_str = "DircFilter\n"
        for key, value in vars(self).items():
            if value:
                cond_str += " - " + key + " : [" + ",".join(value) + "]\n"

        return cond_str
