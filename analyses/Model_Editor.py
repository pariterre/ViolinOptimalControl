# coding: utf-8
import os.path
from ConvertModel import *
from ConvertOsim2Biorbd import *

try:
    # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
except:
    # Python 2
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog


class ToolMenu(tk.Menu):
    def __init__(self, mainmenubar, *args, ** kwargs):
        tk.Menu.__init__(self, mainmenubar, *args, **kwargs)
        self.mainmenubar = mainmenubar


class MainMenuBar(tk.Menu):
    def __init__(self, parent, *args, ** kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)
        self.config(tearoff=0)
        self.parent = parent


class MainWindow(tk.Tk):
    def __init__(self, *args, ** kwargs):
        # heritance of tk window
        tk.Tk.__init__(self, *args, **kwargs)
        # general window
        self.title("Biorbd Model Converter")
        self.geometry("%dx%d%+d%+d" % (1000, 100, 350, 125))

        # menu bar
        self.main_menu_bar = MainMenuBar(self)

        self.menu1 = ToolMenu(self.main_menu_bar, tearoff=0)
        self.menu1.add_command(label="", command=self.fun('Create'))
        self.menu1.add_command(label="Edit", command=self.fun('Edit'))
        self.menu1.add_separator()
        self.menu1.add_command(label="Quit", command=self.quit)
        self.main_menu_bar.add_cascade(label="File", menu=self.menu1)

        self.menu2 = ToolMenu(self.main_menu_bar, tearoff=0)
        self.menu2.add_command(label="1", command=self.fun('*'))
        self.menu2.add_command(label="2", command=self.fun('*'))
        self.menu2.add_command(label="3", command=self.fun('*'))
        self.main_menu_bar.add_cascade(label="Analyse", menu=self.menu2)

        self.menu3 = ToolMenu(self.main_menu_bar, tearoff=0)
        self.menu3.add_command(label="About", command=self.fun('*'))
        self.main_menu_bar.add_cascade(label="Help", menu=self.menu3)

        self.config(menu=self.main_menu_bar)

        # Initializing
        self.file_type = 'None'
        self.is_checked = False
        self.original_path = ''
        self.biorbd_path = ''
        self.initial_dir = os.getcwd()
        self.filename = ''
        self.check_status = 'file not found'
        self.file_exist = False
        self.unknown_extension = False
        self.model = None
        self.is_analyzed = False

        # General frame for file management
        self.general_frame = tk.Frame(self, height=100)
        self.general_frame.pack(fill=tk.BOTH)

        # Frame for analysis
        self.frame_analyse = tk.Frame(self, borderwidth=4, relief=tk.GROOVE)
        self.label_analyse = tk.Label(self.frame_analyse, text="Analyse file", borderwidth=2, relief=tk.GROOVE)
        self.tree = ttk.Treeview(self.frame_analyse, columns=('name', 'size', 'modified'))

        # Frame for original model
        self.frame_original = tk.Frame(self.general_frame, borderwidth=4, relief=tk.GROOVE)
        self.frame_original.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
        self.label_original = tk.Label(self.frame_original, text="Original Model", borderwidth=2, relief=tk.GROOVE)
        self.label_original.pack()

        # Frame for converted model
        self.frame_converted = tk.Frame(self.general_frame, borderwidth=4, relief=tk.GROOVE)
        self.frame_converted.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
        self.label_converted = tk.Label(self.frame_converted, text="Converted Model", borderwidth=2, relief=tk.GROOVE)
        self.label_converted.pack()

        # Frame for exportation
        self.frame_exportation = tk.Frame(self.general_frame, borderwidth=4, relief=tk.GROOVE)
        self.frame_exportation.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
        self.label_exportation = tk.Label(self.frame_exportation, text="Exportation", borderwidth=2, relief=tk.GROOVE)
        self.label_exportation.pack()

        # Quit button
        self.button_quit = tk.Button(self, text="Quit", command=self.quit)
        self.button_quit.pack(side=tk.BOTTOM)

        # entry
        self.value = tk.StringVar()
        self.value.set("Enter path of original model")
        self.entree = tk.Entry(self.frame_original, textvariable=self.value, width=20)
        self.entree.pack(side=tk.LEFT)
        self.entree.focus_set()

        # Find path
        self.path_to_find = tk.StringVar()
        self.find_path_button = tk.Button(self.frame_original, text='Find', width=5, command=self.find_path)
        self.find_path_button.pack(side=tk.LEFT)

        # Check path
        self.check_button = tk.Button(self.frame_original, text="Check path", width=10, command=self.check_path)
        self.check_button.pack(side=tk.LEFT)

        self.status = tk.Label(self.frame_original, text="File found : " + self.file_type)
        self.status.pack(side=tk.BOTTOM)

        self.analyse_button =\
            tk.Button(self.frame_original, text='Analyse file', command=self.analyse, state=tk.DISABLED)
        self.analyse_button.pack(side=tk.BOTTOM)

    def fun(self, name):
        def _fun():
            print(name)
        return _fun

    def find_path(self):
        self.filename = filedialog.askopenfilename(initialdir=self.initial_dir, title="Select file",
                                                   filetypes=(("bioMod files", "*.bioMod"),
                                                              ("S2mMod files", "*.s2mMod"), ("OpenSimfiles", "*.osim"),
                                                              ("all files", "*.*")))
        self.value.set(os.path.relpath(self.filename))

    def check(self, _window, is_error=False):
        def _check():
            _window.destroy()
            self.status.config(text="File found : " + self.file_type)
            if is_error:
                self.analyse_button.config(state=tk.DISABLED)
            else:
                self.is_checked = True
                self.analyse_button.config(state=tk.NORMAL)

        return _check

    def unknown_extension_check(self):
        res = self.var1.get()
        if res == 'Biorbd file (.bioMod)':
            self.file_type = 'Biorbd'
            self.is_checked = True
            self.status.config(text="File found : " + self.file_type)
            self.analyse_button.config(state=tk.NORMAL)
            self.top.destroy()
            return 0
        elif res == 'OpenSim file (.osim)':
            self.file_type = 'OpenSim'
            self.is_checked = True
            self.status.config(text="File found : " + self.file_type)
            self.analyse_button.config(state=tk.NORMAL)
            self.top.destroy()
            return 0
        else:
            error_window = tk.Toplevel()
            error_window.geometry("%dx%d%+d%+d" % (300, 160, 250, 125))
            error_window.title("Error")
            label_error = tk.LabelFrame(error_window, text="Message", padx=20, pady=20)
            label_error.pack(fill="both", expand="yes")
            tk.Label(label_error, text="You must choose a type of file").pack()
            tk.Button(label_error, text="Ok", command=self.check(error_window, True)).pack()

    def check_path(self):
        self.file_type = 'None'
        self.original_path = self.entree.get()
        if os.path.exists(self.original_path):
            if self.original_path.find('.osim') > -1:
                self.check_status = 'OpenSim file found'
                self.file_exist = True
                self.unknown_extension = False
                self.file_type = 'OpenSim'
            elif self.original_path.find('.bioMod') > -1:
                self.check_status = 'Biorbd file found'
                self.file_exist = True
                self.unknown_extension = False
                self.file_type = 'Biorbd'
            elif self.original_path.find('.biomod') > -1:
                self.check_status = 'Biorbd file found'
                self.file_exist = True
                self.unknown_extension = False
                self.file_type = 'Biorbd'
            else:
                self.check_status = 'file found but extension is not recognized.\n' \
                               'Please indicate the type of file : '
                self.file_exist = True
                self.unknown_extension = True
        else:
            self.check_status = 'file not found'
            self.file_exist = False
            self.unknown_extension = False

        # Message box
        self.top = tk.Toplevel()
        self.top.geometry("%dx%d%+d%+d" % (300, 160, 250, 125))
        self.top.title("File checker")
        label_top = tk.LabelFrame(self.top, text="Message", padx=20, pady=20)
        label_top.pack(fill="both", expand="yes")
        tk.Label(label_top, text=self.check_status).pack()

        if self.unknown_extension:
            var1 = tk.StringVar()
            options = ["Biorbd file (.bioMod)", "OpenSim file (.osim)"]
            list_file = tk.OptionMenu(label_top, var1, *options)
            var1.set('Choose a file type')  # default value
            list_file.pack()
            button_quit = tk.Button(label_top, text="Ok", command=self.unknown_extension_check)
            button_quit.pack(side=tk.BOTTOM)
        else:
            if self.file_exist:
                button_quit = tk.Button(label_top, text="Ok", command=self.check(self.top))
                button_quit.pack()
            else:
                button_quit = tk.Button(label_top, text="Ok", command=self.check(self.top, True))
                button_quit.pack()
        if self.file_exist and self.is_checked:
            self.status.config(text="File found : " + self.file_type)

    def actualise_file(self):
        print('***')
        print(self.file_type)
        if self.file_type == 'OpenSim':
            self.biorbd_path = self.original_path[-2:]+'-converted.bioMod'
            print('** opensim file')
            try:
                ConvertedFromOsim2Biorbd3(self.biorbd_path, self.original_path)
                return BiorbdModel(self.biorbd_path)

            except:
                ConvertedFromOsim2Biorbd4(self.biorbd_path, self.original_path)
                return BiorbdModel(self.biorbd_path)
        elif self.file_type == 'Biorbd':
            self.biorbd_path = self.original_path
            print('** biorbd file')
            try:
                return BiorbdModel(self.biorbd_path)
            except:
                print('*')

    def analyse(self):
        self.model = self.actualise_file()
        self.model.read()
        # Frame for analyse
        if not self.is_analyzed:
            self.geometry("%dx%d%+d%+d" % (1000, 400, 350, 125))
            self.frame_analyse.pack(side=tk.BOTTOM, fill=tk.BOTH, expand='yes')
            self.label_analyse.pack()
            self.is_analyzed = True

        index_model = self.tree.insert('', 'end', 'Model', text='Model')
        index_segments = self.tree.insert(index_model, 0, 'Segments', text='Segments')
        index_muscle_groups = self.tree.insert(index_model, 1, 'MuscleGroups', text='MuscleGroups')

        index = 3
        for segment in self.model.get_segments():
            print(index)
            index_segment = self.tree.insert(index_segments, 'end', segment.get_name(),
                                             text='segment '+segment.get_name())
            for marker in segment.get_markers():
                index = self.tree.insert(index_segment, 'end', marker.get_name(), text='marker '+marker.get_name())
        for muscle_group in self.model.get_muscle_groups():
            index_muscle_group = \
                self.tree.insert(index_muscle_groups, 'end', muscle_group.get_name(),
                                 text='muscle group '+muscle_group.get_name())
            for muscle in muscle_group.get_muscles():
                index_muscle = \
                    self.tree.insert(index_muscle_group, 'end', muscle.get_name(), text='muscle '+muscle.get_name())
                for pathpoint in muscle.get_pathpoints():
                    index = self.tree.insert(index_muscle, 'end', pathpoint.get_name(),
                                             text='pathpoint '+pathpoint.get_name())
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand='yes')

    def state(self, boolean):
        if boolean:
            self.analyse_button.config(state=tk.NORMAL)


if __name__ == "__main__":

    main_window = MainWindow()
    main_window.mainloop()


