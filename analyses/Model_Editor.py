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


file_type = 'None'
is_checked = False
original_path = ''
biorbd_path = ''
initial_dir = os.getcwd()
check_status = 'file not found'
file_exist = False
unknown_extension = False
model = None


def callback():
    print(entree.get())


def fun(name):
    def _fun():
        print(name)
    return _fun


def find_path():
    window.filename = filedialog.askopenfilename(initialdir=initial_dir, title="Select file",
                                                 filetypes=(("bioMod files", "*.bioMod"), ("S2mMod files", "*.s2mMod"), ("OpenSimfiles", "*.osim"), ("all files","*.*")))
    value.set(os.path.relpath(window.filename))


def check(_window, is_error=False):
    def _check():
        _window.destroy()
        status.config(text="File found : " + file_type)
        if is_error:
            analyse_button.config(state=tk.DISABLED)
        else:
            is_checked = True
            analyse_button.config(state=tk.NORMAL)

    return _check


def check_path():
    file_type = 'None'
    original_path = entree.get()
    if os.path.exists(original_path):
        if original_path.find('.osim') > -1:
            check_status = 'OpenSim file found'
            file_exist = True
            unknown_extension = False
            file_type = 'OpenSim'
        elif original_path.find('.bioMod') > -1:
            check_status = 'Biorbd file found'
            file_exist = True
            unknown_extension = False
            file_type = 'Biorbd'
        elif original_path.find('.biomod') > -1:
            check_status = 'Biorbd file found'
            file_exist = True
            unknown_extension = False
            file_type = 'Biorbd'
        else:
            check_status = 'file found but extension is not recognized.\n' \
                           'Please indicate the type of file : '
            file_exist = True
            unknown_extension = True
    else:
        check_status = 'file not found'
        file_exist = False
        unknown_extension = False

    # Message box
    top = tk.Toplevel()
    top.geometry("%dx%d%+d%+d" % (300, 160, 250, 125))
    top.title("File checker")
    l = tk.LabelFrame(top, text="Message", padx=20, pady=20)
    l.pack(fill="both", expand="yes")
    tk.Label(l, text=check_status).pack()

    def unknown_extension_check():
        res = var1.get()
        if res == 'Biorbd file (.bioMod)':
            file_type = 'Biorbd'
            is_checked = True
            status.config(text="File found : " + file_type)
            analyse_button.config(state=tk.NORMAL)
            top.destroy()
            return 0
        elif res == 'OpenSim file (.osim)':
            file_type = 'OpenSim'
            is_checked = True
            status.config(text="File found : " + file_type)
            analyse_button.config(state=tk.NORMAL)
            top.destroy()
            return 0
        else:
            error_window = tk.Toplevel()
            error_window.geometry("%dx%d%+d%+d" % (300, 160, 250, 125))
            error_window.title("Error")
            label_error = tk.LabelFrame(error_window, text="Message", padx=20, pady=20)
            label_error.pack(fill="both", expand="yes")
            tk.Label(label_error, text="You must choose a type of file").pack()
            tk.Button(label_error, text="Ok", command=check(error_window, True)).pack()

    if unknown_extension:
        var1 = tk.StringVar()
        options = ["Biorbd file (.bioMod)", "OpenSim file (.osim)"]
        list_file = tk.OptionMenu(l, var1, *options)
        var1.set('Choose a file type')  # default value
        list_file.pack()
        button_quit = tk.Button(l, text="Ok", command=unknown_extension_check)
        button_quit.pack(side=tk.BOTTOM)
    else:
        if file_exist:
            button_quit = tk.Button(l, text="Ok", command=check(top))
            button_quit.pack()
        else:
            button_quit = tk.Button(l, text="Ok", command=check(top, True))
            button_quit.pack()
    if file_exist and is_checked:
        status.config(text="File found : " + file_type)

# TODO create a button to launch conversion


def actualise_file():
    print('***')
    print(file_type)
    if file_type == 'OpenSim':
        biorbd_path = original_path[-2:]+'-converted.bioMod'
        print('** opensim file')
        try:
            ConvertedFromOsim2Biorbd3(biorbd_path, original_path)
            return BiorbdModel(biorbd_path)

        except:
            ConvertedFromOsim2Biorbd4(biorbd_path, original_path)
            return BiorbdModel(biorbd_path)
    elif file_type == 'Biorbd':
        biorbd_path = original_path
        print('** biorbd file')
        try:
            return BiorbdModel(biorbd_path)
        except:
            print('*')


def analyse():
    print('analysed')
    model = actualise_file()
    model.read()
    # Frame for analyse
    window.geometry("%dx%d%+d%+d" % (1000, 400, 350, 125))
    frame_analyse = tk.Frame(window, borderwidth=4, relief=tk.GROOVE)
    frame_analyse.pack(side=tk.BOTTOM, fill=tk.BOTH, expand='yes')
    label_analyse = tk.Label(frame_analyse, text="Analyse file", borderwidth=2, relief=tk.GROOVE)
    label_analyse.pack()
    tree = ttk.Treeview(frame_analyse)
    index_model = tree.insert('', 'end', 'Model', text='Model')
    index_segments = tree.insert(index_model, 0, 'Segments', text='Segments')
    index_muscle_groups = tree.insert(index_model, 1, 'MuscleGroups', text='MuscleGroups')
    segment_index = 0
    for segment in model.get_segments():
        tree.insert(index_segments, segment_index, segment.get_name(), text=segment.get_name())
        marker_index = 0
        for marker in segment.get_markers():
            tree.insert(segment_index, marker_index, marker.get_name(), text=marker.get_name())
            marker_index += 1
        segment_index += 1
    muscle_group_index = 0
    for muscle_group in model.get_muscle_groups():
        tree.insert(index_muscle_groups, muscle_group_index, muscle_group.get_name(), text=muscle_group.get_name())
        muscle_index = 0
        for muscle in muscle_group.get_muscles():
            tree.insert(muscle_group_index, muscle_index, muscle.get_name(), text=muscle.get_name())
            pathpoint_index = 0
            for pathpoint in muscle.get_pathpoints():
                tree.insert(muscle_index, pathpoint_index, pathpoint.get_name(), text=pathpoint.get_name())
                pathpoint_index += 1
            muscle_index += 1
        muscle_group_index += 1
    tree.pack()

def state(boolean):
    if boolean:
        analyse_button.config(state=tk.NORMAL)


window = tk.Tk()
window['bg']='white'
window.title("Biorbd Model Converter")
window.geometry("%dx%d%+d%+d" % (1000, 100, 350, 125))

# Menu bar
menu_bar = tk.Menu(window)
menu1 = tk.Menu(menu_bar, tearoff=0)
menu1.add_command(label="Create", command=fun('Create'))
menu1.add_command(label="Edit", command=fun('Edit'))
menu1.add_separator()
menu1.add_command(label="Quit", command=window.quit)
menu_bar.add_cascade(label="File", menu=menu1)

menu2 = tk.Menu(menu_bar, tearoff=0)
menu2.add_command(label="1", command=fun('*'))
menu2.add_command(label="2", command=fun('*'))
menu2.add_command(label="3", command=fun('*'))
menu_bar.add_cascade(label="Analyse", menu=menu2)

menu3 = tk.Menu(menu_bar, tearoff=0)
menu3.add_command(label="About", command=fun('*'))
menu_bar.add_cascade(label="Help", menu=menu3)

window.config(menu=menu_bar)


# General frame for file management
general_frame = tk.Frame(window, height=100)
general_frame.pack(fill=tk.BOTH)

# Frame for original model
frame_original = tk.Frame(general_frame, borderwidth=4, relief=tk.GROOVE)
frame_original.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
label_original = tk.Label(frame_original, text="Original Model", borderwidth=2, relief=tk.GROOVE)
label_original.pack()

# Frame for converted model
frame_converted = tk.Frame(general_frame, borderwidth=4, relief=tk.GROOVE)
frame_converted.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
label_converted = tk.Label(frame_converted, text="Converted Model", borderwidth=2, relief=tk.GROOVE)
label_converted.pack()

# Frame for exportation
frame_exportation = tk.Frame(general_frame, borderwidth=4, relief=tk.GROOVE)
frame_exportation.pack(side=tk.LEFT, fill=tk.BOTH, expand='yes')
label_exportation = tk.Label(frame_exportation, text="Exportation", borderwidth=2, relief=tk.GROOVE)
label_exportation.pack()

# Quit button
button = tk.Button(window, text="Quit", command=window.quit)
button.pack(side=tk.BOTTOM)

# entry
value = tk.StringVar()
value.set("Enter path of original model")
entree = tk.Entry(frame_original, textvariable=value, width=20)
entree.pack(side=tk.LEFT)
entree.focus_set()

# Find path
path_to_find = tk.StringVar()
find_path_button = tk.Button(frame_original, text='Find', width=5, command=find_path)
find_path_button.pack(side=tk.LEFT)

# Check path
check_button = tk.Button(frame_original, text="Check path", width=10, command=check_path)
check_button.pack(side=tk.LEFT)

status = tk.Label(frame_original, text="File found : "+file_type)
status.pack(side=tk.BOTTOM)

analyse_button = tk.Button(frame_original, text='Analyse file', command=analyse, state=tk.DISABLED)
analyse_button.pack(side=tk.BOTTOM)


window.mainloop()

