"""
gui/_dnd_ctk.py

Project: WebUntisAbsenceDashboard
"""

from tkinterdnd2 import DND_FILES, TkinterDnD
from customtkinter import CTk
from typing import Any, Tuple, Callable
from shutil import copy
from os import path, makedirs
from re import findall


##################################################
#                     Code                       #
##################################################

class DragNDropCTk(CTk, TkinterDnD.DnDWrapper):
    """
    CTk with Drag and Drop functionality
    """
    __data_dir: str
    __DROP_CALLBACK_TYPE = Callable[[list[str]], Any]
    __drop_callback: __DROP_CALLBACK_TYPE

    def __init__(self, data_dir: str, drop_callback: __DROP_CALLBACK_TYPE, *args: Any, **kwargs: Any) -> None:
        """
        Init CTk-Window with Drag and Drop functionality

        :param args: Additional positional arguments to be passed to the superclass initializer.
        :param kwargs: Additional keyword arguments to be passed to the superclass initializer.
        """
        super().__init__(*args, **kwargs)
        TkinterDnD._require(self)

        self.__data_dir = data_dir
        self.__drop_callback = drop_callback

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.__on_drop)

    def __on_drop(self, event: TkinterDnD.DnDEvent) -> None:
        """
        Handles the drop event
        :param event: Contains data regarding dropped files
        """
        matches: list[Tuple[str, str]] = findall(r'\{([^}]+)\}|(\S+)', event.data)
        dropped_files: list[str] = [grp1 if grp1 else grp2 for grp1, grp2 in matches]

        makedirs(self.__data_dir, exist_ok=True)

        destinations: list[str] = []
        for file_path in dropped_files:
            destination: str = path.join(self.__data_dir, path.basename(file_path))
            copy(file_path, destination)
            destinations.append(destination)

        self.__drop_callback(destinations)
