"""
gui/_drop_messagebox.py

Project: WebUntisAbsenceDashboard
"""

from customtkinter import CTkToplevel, CTkButton, CTkLabel


##################################################
#                     Code                       #
##################################################

class DropMessageBox(CTkToplevel):
    """
    MessageBox for selecting an option when dropping files
    """
    __info_label: CTkLabel

    __add_button: CTkButton
    __new_button: CTkButton
    __cancel_button: CTkButton

    def __init__(self) -> None:
        super().__init__()

        self.__info_label = CTkLabel(self, text="INFO")

        self.__add_button = CTkButton(self, text="Add")
        self.__new_button = CTkButton(self, text="New (Replace)")
        self.__cancel_button = CTkButton(self, text="Cancel")

        self.__info_label.grid(row=0, column=0, column_span=3, sticky="NSEW")
        self.__add_button.grid(row=1, column=0)
        self.__new_button.grid(row=1, column=1)
        self.__cancel_button.grid(row=1, column=2)

        self.grid_rowconfigure("all", weight=1),
        self.grid_columnconfigure("all", weight=1)

    def choose_button(self) -> None:
        ...
