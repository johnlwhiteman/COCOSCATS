import sys
from tkinter import END, messagebox, Menu, Text, Tk, WORD, Y
import traceback
from Core.Msg import Msg

class Editor(object):

    def __init__(self):
        self.__root = Tk()
        self.__root.title("COCOSCATS Editor")
        self.__root.bind_all('<Control-Key-s>', self.__save)
        self.__root.bind_all('<Control-Key-n>', self.__next)
        self.__root.bind_all('<Control-Key-a>', self.__abort)
        self.__mainMenu = Menu(self.__root)
        self.__root.config(menu=self.__mainMenu)
        self.__mainMenu.add_command(label="Save",
                                    underline=1,
                                    command=self.__save)
        self.__mainMenu.add_command(label="Next",
                                    underline=1,
                                    command=self.__next)
        self.__mainMenu.add_command(label="Abort",
                                    underline=1,
                                    command=self.__abort)
        self.__root.protocol("WM_DELETE_WINDOW", self.__abort)

    def __abort(self, event=None):
        Msg.showAbort("Script did not complete execution.")
        sys.exit(1)

    def __handleException(self, msg, abortFlag=True):
        messagebox.showerror("COCOSCATS", msg)
        Msg.showError(msg)
        if abortFlag:
            self.__root.destroy()
            sys.stderr.flush()
            sys.exit(1)

    def __next(self, event=None):
        if self.__text.edit_modified():
            response = messagebox.askyesnocancel("COCOSCATS", "Save it or not")
            if response is None:
                return
            if response is True:
                self.__save()
        self.__root.destroy()

    def __open(self):
        try:
            with open(self.__inputPath, "r", encoding="utf8") as fd:
                self.__text.insert("end", fd.read())
        except IOError as e:
            self.__handleException(e, True)

    def run(self, inputPath, outputPath):
        self.__inputPath = inputPath
        self.__outputPath = outputPath
        self.__root.title("COCOSCATS EDITOR: {0}".format(self.__outputPath))
        self.__text = Text(self.__root, wrap=WORD)
        self.__text.pack(fill=Y, expand=1)
        self.__open()
        self.__text.focus_set()
        self.__text.edit_modified(False)
        self.__root.mainloop()

    def __save(self, event=None):
        try:
            with open(self.__outputPath, "w", encoding="utf8") as fd:
                fd.write(self.__text.get(0.0, END+'-1c'))
                self.__text.edit_modified(False)
        except IOError as e:
            self.__handleException(e, True)

