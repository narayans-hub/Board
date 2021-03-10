import functools
import importlib
import inspect
import sys
import threading
import tkinter as tk
from os import path
from tkinter import *
from tkinter import Tk, Entry, Label, StringVar
from tkinter import filedialog
from typing import Any, Tuple


class WriteLabel(Label):
    """
    Just a writable label widget.
    """

    def __init__(self, owner, master: Any = None, *args: Tuple[Any], **kwargs: Any):
        """
        Constructor.

        :param master:  The parent of the widget.
        :type master:   Any.

        :param args:    Additional positional arguments.
        :type args:     Tuple[Any].

        :param kwargs:  Additional keyword arguments.
        :type kwargs:   Any.
        """
        super().__init__(*args, master=master, **kwargs)

        self._parent = master
        self._owner = owner
        self._value = StringVar()
        self._entry_value = StringVar()

        if 'text' in kwargs:
            self._value.set(kwargs['text'])
            self._entry_value.set(kwargs['text'])

        self.config(
            textvariable=self._value,
            relief='raised'
        )

        self._entry = Entry(
            textvariable=self._entry_value,
            justify='center'
        )

        self.behaviours()
        self.update()

    def set_label(self, label):
        self._value.set(label)
        self._entry_value.set(label)
        self.config(textvariable=self._value)

    def get_label(self):
        return self._value.get()

    def behaviours(self) -> None:
        """
        Sets the binding for interested events by defining the behaviour of the widget.

        :return: None.
        :rtype: None.
        """
        self.bind('<Button-1>', self.handle)
        self.bind('<Shift-1>', self.edit)
        self.bind('<Configure>', self.save)
        self._entry.bind('<FocusOut>', self.save)
        self._entry.bind('<Return>', self.save)

    def handle(self, _):
        self._owner.handle(self)

    def edit(self, _) -> None:
        """
        It places the entry as overlay on top of the current widget.

        :param _:   The event object [unused].
        :type _:    Event.

        :return: None.
        :rtype: None.
        """
        self._entry.place_forget()
        self._entry_value.set(value=self._value.get())
        self._entry.place(
            x=self.winfo_x(),
            y=self.winfo_y(),
            width=self.winfo_width(),
            height=self.winfo_height()
        )
        self._entry.focus_set()

    def save(self, _) -> None:
        """
        It hides the entry and copy its actual value to the current widget.

        :param _:   The event object [unused].
        :type _:    Event.

        :return: None.
        :rtype: None.
        """
        self._entry.place_forget()
        self._value.set(value=self._entry_value.get())
        self.update()


class GameCell(WriteLabel):

    def __init__(self, root, owner, row, col, label=""):
        self.baseFont = ("Times", 12)
        # Call the constructor in the parent class: Button|WriteLabel
        WriteLabel.__init__(self, owner, root, text=label, width=3, height=2, relief=GROOVE, font=self.baseFont)
        self.label = label
        self.color = root.cget('bg')  # default tkinter root window color

        self.row = row
        self.col = col
        self.show(root)

    def get_row(self):
        '''
        Returns the row number (0-based) within the gameboard of this cell
        :return: the row number of this cell
        '''
        return self.row

    def get_col(self):
        '''
        Returns the column number (0-based) within the gameboard of this cell
        :return:
        '''
        return self.col

    def reset(self):
        self.set_color("gray")
        self.set_label(self.label)

    def set_color(self, c):
        '''
        Assigns a specified color to this cell
        :param c: color to be assigned to cell, for example "RED"
        :return:
        '''
        self.color = c
        self.configure(bg=self.color)

    def get_color(self):
        '''
        Returns the current color of this cell
        :return: current color of this cell, for example "RED"
        '''
        return self.color

    def show(self, root):
        self.isFaceUp = True
        self.config(text=self.label, font=("Arial", 18))
        root.update()  # update root so that the cell is repainted immediately

    def hide(self):
        self.configure(text="", bg='LIGHT GRAY')
        self.isFaceUp = False


class GameBoard(object):
    """
    :author: Sridhar Narayan
    :version: 1.0 - December 2020

    :contact: narayans@uncw.edu
    :organization: University of North Carolina Wilmington

    :summary: Support for a gameboard-like interface

    """
    __gameboard = None

    @staticmethod
    def get_board():
        return GameBoard.__gameboard

    def get_cell(self, row, col):
        '''
        Returns the cell at the specified row,col location
        :param row: row number (0-based)
        :param col: column number (0-based)
        :return: cell at the specified location within the gameboard
        '''
        cell_offset = row * self.num_columns + col
        return self.cells[cell_offset]

    def get_row_count(self):
        '''
        Return the number of rows in the gameboard
        :return: the number of rows in the gameboard
        '''
        return self.num_rows

    def get_column_count(self):
        '''
        Return the number of columns in the gameboard
        :return: the number of columns in the gameboard
        '''
        return self.num_columns

    def reset(self):
        for c in self.cells:
            c.reset()

    def set_color(self, r, c, color):
        cell = self.get_cell(r, c)

        cell.set_color(color)

    def get_color(self, r, c):
        cell = self.get_cell(r, c)

        return cell.get_color()

    def set_label(self, r, c, label):
        '''
        set label of cell at location r,c to label
        Args:
            r: row number
            c: column number
            label: label

        Returns: Nothing

        '''
        cell = self.get_cell(r, c)

        cell.set_label(label)

    def get_label(self, r, c):
        cell = self.get_cell(r, c)

        return cell.get_label()

    def __set_size(self, num_rows, num_cols):
        self.CardType = GameCell  # what kind of card
        self.num_rows = num_rows
        self.num_columns = num_cols

        self.__build_ui()
        self.__main_root.update()
        self.__maybe_load_code()

    def __init__(self, num_rows=4, num_columns=4, title="Game Board", threaded=True, start=None, handle=None):

        self.__main_root = Tk()
        _width = 600
        _height = 400
        self.__main_root.config(width=_width, height=_height)
        # Disable resizing
        # self.__main_root.resizable(0,0)
        self.__main_root.title(title)

        self.__threaded = threaded  # default True - code is run in separate thread
        self.__handle = handle  # default None - no event handler
        self.__start = start  # default None - no startup code

        self.opsMenu = None
        self.__active_key = None
        GameBoard.__gameboard = self

        self.__set_size(num_rows, num_columns)

        if self.__start is not None:  # run this function on startup
            # self.__exec_task(start)
            self.__start()

        self.__main_root.mainloop()

    # returns current list of labels under menu option opsMenu
    @staticmethod
    def __menu_options(menu_item):
        mx = menu_item.index(tk.END)
        if mx is None:
            return []
        else:
            return [menu_item.entrycget(i, 'label') for i in range(mx + 1)]

    # open specified file and determine module
    def __load_file(self, code_file_name, message):
        folder, filename = code_file_name.rsplit('/', 1)
        if folder not in sys.path:
            sys.path.append(folder)
        module_name = filename.split('.')[0]
        self.currentModuleName = module_name

        mod = importlib.import_module(module_name)
        # open_file, file_name, description = imp.find_module(module_name)
        # module = imp.load_module(code_file_name, open_file, file_name, description)

        if message == "Reloaded":
            importlib.reload(mod)  # refresh module definition if reloading
        self.__load_functions(mod)  # self.currentModule)# module

    # load student code
    def __load_code(self):
        code_file_types = [("Python files", "*.py")]
        code_file_name = filedialog.askopenfilename(filetypes=code_file_types)
        if len(code_file_name) > 0:
            self.currentCodeFileName = code_file_name
            self.__load_file(code_file_name, "Loaded")

    # reload the currently loaded code file
    def __reload_code(self):
        if self.currentCodeFileName is not None:
            # noinspection PyTypeChecker
            # self.__show_message("Reloaded code from " + self.currentCodeFileName)
            self.__load_file(self.currentCodeFileName, "Reloaded")

    # update the code binding (definition) for the specified function
    def __update_func_def(self, func_to_update):
        functions = inspect.getmembers(self.currentModule, inspect.isfunction)

        for f in functions:
            func_name = f[0]
            func_code = f[1]
            w_list = str(func_to_update).split()
            if func_name == w_list[1]:  # have we found the function def of interest?
                return func_code  # if so, return the current definition for that function

    # create and start a threaded task when called
    def __exec_task(self, f):
        self.__reload_code()  # reload the function definition file
        f = self.__update_func_def(f)  # update the binding of the function of interest
        if self.__threaded:  # default behavior
            threading.Thread(target=f).start()  # execute that function in own thread
        else:  # handles situations that are not thread safe
            f()  # execute function in current thread

    # load the user code contained in the file from which the viewer was instantiated
    def __maybe_load_code(self):
        main_mod = sys.modules['__main__']
        self.currentModule = main_mod

        if hasattr(main_mod, '__file__'):  # launched by executing a Python script
            self.currentCodeFileName = path.abspath(sys.modules['__main__'].__file__)
            self.currentCodeFileName = self.currentCodeFileName.replace('\\', '/')
            self.__load_functions(main_mod)

    # add functions defined in specified file to myOps menu
    def __load_functions(self, module):  # message):
        self.currentModule = module
        functions = inspect.getmembers(module, inspect.isfunction)

        current_menu_options = self.__menu_options(self.opsMenu)

        for f in functions:
            f_label = f[0]
            if f_label[0:2] == '__':
                continue  # skip over the 'private' functions
            f_name = f[1]
            # command associated with this menu option includes the function to be
            # executed as a part of the task as a parameter
            # functools.partial is necessary for this
            # since it allows a partially specified command to be set as the target of the menu action
            # duplicate labels not allowed
            if f_label in current_menu_options:  # delete option before updating
                index = current_menu_options.index(f_label)
                self.opsMenu.delete(index)
                current_menu_options.remove(f_label)

            # update existing option, or add new one
            self.opsMenu.add_command(label=f_label, command=functools.partial(self.__exec_task, f_name))

    # start a new game
    def new_game(self, card_type):
        for child in self.__main_root.winfo_children():
            child.destroy()  # remove all old cards

        GameBoard(self.num_rows, self.num_columns)

    def __build_menu(self, root):
        menubar = Menu(root)

        game_menu = Menu(menubar, tearoff=0)

        load_menu = Menu(menubar, tearoff=0)
        load_menu.add_command(label="Load", command=self.__load_code)
        load_menu.add_command(label="Reload", command=self.__reload_code)

        game_menu.add_command(label="Exit", command=root.destroy)
        menubar.add_cascade(label="Game", menu=game_menu)
        menubar.add_cascade(label="Code", menu=load_menu)

        self.opsMenu = Menu(menubar, tearoff=0)

        # add sub-menus to menubar
        menubar.add_cascade(label="MyFuncs", menu=self.opsMenu)

        root.config(menu=menubar)

    def handle(self, clicked_cell):
        if self.__handle is not None:  # if an event handler is specified, invoke it
            self.__handle(clicked_cell)

    def __build_ui(self):
        for child in self.__main_root.winfo_children():
            child.destroy()  # remove all old cards
        self.cells = []

        count = 0
        for r in range(self.num_rows):
            Grid.rowconfigure(self.__main_root, r, weight=1)
            for c in range(self.num_columns):
                Grid.columnconfigure(self.__main_root, c, weight=1)

                c1 = GameCell(self.__main_root, self, r, c)

                self.cells.append(c1)  # add card to the cells list

                self.cells[count].grid(row=r, column=c, padx=5, pady=5, sticky=N + S + E + W)
                count = count + 1

        self.__build_menu(self.__main_root)

# only do this if invoked as application
# if __name__ == '__main__':
# GameBoard(8,8)
