#!/usr/bin/env python3
'''
Recipe Scribe
version 1.1
Basic no frills GUI Program for creating and saving recipes.
Written in Python 3.6 and TKinter
 
Copyright (C) 2019 Clay Davenport
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import filedialog
import re
import configparser
from os import path
import ToolTip as tt
from HelpText import help_text
from AboutText import about_text

root = tk.Tk()
'''
The next 4 Lines deal with the program icon that displays in the
active window and the dock as well as allowing PyInstaller
to reference the file properly.
Executables created with Pyinstaller create a path for the program in /tmp
when run. 
This breaks the relative path to the icon file.
'''
rootdir = path.dirname(__file__) # Get the Pyinstaller root path
icon = path.join(rootdir, 'rc.png') # join the path to the icon file
img = tk.PhotoImage(file=icon) # Set the program icon
root.iconphoto(False, img) # Display the program icon

width = int(root.winfo_screenwidth() / 1.9)
height = int(root.winfo_screenheight() / 1.2)
root.geometry('%sx%s' % (width, height))
root.configure(background = 'gray0')
root.rowconfigure(0, weight = 1)
root.rowconfigure(1, weight = 1)
root.columnconfigure(0, weight = 1)
root.columnconfigure(1, weight = 3)
style = ttk.Style()


config = configparser.ConfigParser()

# Set the variables from the config file if it exists
# If not create it with the default values

if path.exists("CONFIG"):
    config.read("CONFIG")
    save_path = config.get('DefaultSavePath', 'save_path')
    use_bp = config.get('UseBulletPoints', 'use_bp')
    fn_format = config.get('FormatFileName', 'fn_format')
    dark_mode = config.get('UseDarkMode', 'dark_mode')
    
else:
    file = open('CONFIG', 'w+')
    file.write("# The options can be changed from the GUI\n")
    file.write("# If editing this file directly:")
    file.write("# Options for UseBulletPoints are True or False\n")
    file.write("# Options for FormatFileName are True or False\n")
    file.write("# Options for UseDarkMode are True or False\n")
    file.write("\n")
    file.close()
    save_path = "None"
    use_bp = "True"
    fn_format = "True"
    dark_mode = "False"
    
    config.add_section("DefaultSavePath")
    config.add_section("UseBulletPoints")
    config.add_section("FormatFileName")
    config.add_section("UseDarkMode")
    config.set("DefaultSavePath", "save_path", "None")
    config.set("UseBulletPoints", "use_bp", "True")
    config.set("FormatFileName", "fn_format", "True")
    config.set("UseDarkMode", "dark_mode", "False")
    with open("CONFIG", "a") as configfile:
        config.write(configfile) 

# Set the color theme for the GUI to avoid ocnflicts with
# other distros and dark themes

if dark_mode == 'False' or dark_mode == 'false':
    background = '#d4d4d4'
    text_color = 'black'
    entry_bg = '#f2f2f2'
    entry_text = 'black'
    label_bg = '#d4d4d4'
    label_text = 'black'
    scroll_color = '#bababa'
    scroll_bg = '#cccccc'
    scrollbar_color = '#858585'
elif dark_mode == 'True' or dark_mode == 'true':
    background = '#343232'
    text_color = 'white'
    entry_bg = '#1e1e1e'
    entry_text = 'white'
    label_bg = '#343232'
    label_text = 'white'
    scroll_color = '#5d5c5c'
    scroll_bg = '#464444'
    scrollbar_color = '#858585'

style.configure('TLabelframe', background = background)
style.configure('TLabelframe.Label', background = background)


class MAIN():
    '''
    The main window where the recipe information is entered
    '''
    def __init__(self, master):
        '''
        Create the root window, call the methods to create
        key bindings and all the widgets
        '''
        self.frame = tk.Frame(root)
        self.frame.pack(fill = 'both', expand = True, side = 'top')
        self.frame.configure(background = background)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 3)
        master.title('Recipe Scribe')
        self.bind_keys()
        self.create_widgets()

    def bind_keys(self):
        '''
        Set the bindings for the keyboard shortcuts to the menu items
        '''
        root.bind('<Control-s>', self._save)
        root.bind('<Control-n>', self._new)
        root.bind('<Control-q>', self._quit)
        root.bind('<Control-h>', HelpWindow)
        root.bind('<Control-c>', DefaultPath)

    def _quit(self, event='q'):
        '''
        Function to exit GUI cleanly
        Bound to the Exit command on the file menu
        '''
        root.quit()
        root.destroy()

    def focus_next_widget(self, event):
        '''
        Allows the use of the TAB key to advance to the next entry field
        '''
        if event.widget == self.title_entered:
            self.ingredients.focus_set()
            return 'break'
        elif event.widget == self.ingredients:
            self.directions.focus_set()
            return 'break'
        elif event.widget == self.directions:
        	self.title_entered.focus_set()
        	return 'break'

    def _save(self, event='s'):
        '''
        _save opens the save dialog box. Not sure if the code is proper here
        Without the event parameter, there's an error using the keyboard
        shortcut (1 param expected, 2 given)
        Without giving event a default value, there's an error when clicking the
        menu item (2 param expected, 1 given)
        '''

        # Retrieve the name of the recipe from the title box widget
        recipe_name = self.title_entered.get()
        # reformat the recipe name for use as the file name
        if fn_format == "True" or fn_format == "true":
            file_name = recipe_name.lstrip().lower().replace(' ', '_')
        else:
            file_name = recipe_name
        # split the ingredient list based on newline
        ingredients = self.ingredients.get(1.0, 'end-1c').split('\n')
        # split the directions based on newline
        directions = self.directions.get(1.0, 'end-1c').split('\n')

        if save_path is None:
            file = filedialog.asksaveasfile(mode='w', initialfile=file_name,
                                            defaultextension=".txt")
        else:
            file = filedialog.asksaveasfile(mode='w', initialfile=file_name,
                                            defaultextension=".txt", initialdir=save_path)
        if file is None:
            return
        file.write('\n')
        file.write(recipe_name)
        file.write('\n\n')
        file.write('Ingredients')
        file.write('\n\n')
        # Make sure blank lines in ingredients or lines beginning with a . are not bullet pointed
        if use_bp =="True" or use_bp == "true":
            for i in ingredients:
                line = i
                if re.match('\.', line):
                    newline = re.sub(r'\.', '', line)
                    file.write(newline + '\n')                  
                elif not re.match('\w', line): # using re import for regex search to see if line contains letters or numbers
                    file.write(line +'\n')
                else:
                    file.write('• ' + line + '\n')  # Prepend each ingredient with a bullet point
        else:
            for i in ingredients:
                line = i
                file.write(line + '\n')
        file.write('\n')
        file.write('Directions')
        file.write('\n\n')
        '''
        Code to automatically indent any line not beginning with a number
        Written as:
        	1. First do this thing.
        	Then do this further thing

        Will be saved as:
        	1. First do this thing.
        	   Then do this further thing

        This makes the directions look better without requiring manual indentation
        However, step 10 and beyond will result in one space of indentation too many.
        Few recipes have more than 9 steps normally. 
        This issue may be looked at later.
        '''
        for i in directions:
            line = i
            if re.match('[1-9]', line):
                file.write(line + '\n')
            elif re.match('\.', line): # Do not indent lines beginning with a period
                newline = re.sub(r'\.', '', line)
                file.write(newline + '\n')
            else:
                file.write('   ' + line + '\n')

        file.write("\n\n\n")
        file.close()

    # Function to clear the text for entering another recipe.
    # See comments for _save for explanation of the event parameter

    def _new(self, event='e'):
        
        self.title_entered.delete(0, 'end')
        self.ingredients.delete(1.0, 'end')
        self.directions.delete(1.0, 'end')
        self.title_entered.focus()  # Place cursor back into the title entry box

    def create_widgets(self):
        '''
        Long method to create all widgets on the root window
        '''

        # Creating a Menu Bar

        menu_bar = Menu(root)
        root.config(menu=menu_bar)
        menu_bar.config(background = background, foreground = text_color)
        # Code for the cascading File menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New   Ctrl+n', command=self._new)
        file_menu.add_separator()
        file_menu.add_command(label='Save  Ctrl+s', command=self._save)
        file_menu.add_separator()
        file_menu.add_command(label='Quit  Ctrl+q', command=self._quit)
        file_menu.configure(background = background, foreground = text_color)
        menu_bar.add_cascade(label='File', menu=file_menu)

        # Code for cascading config menu

        config_menu = Menu(menu_bar, tearoff=0)
        config_menu.add_command(label='Set Default Save Path', command=DefaultPath)
        config_menu.add_separator()
        config_menu.add_command(label='Use Bullet Points (' + use_bp + ')', command=SetBulletPoints)
        config_menu.add_separator()
        config_menu.add_command(label='Format Filename (' + fn_format + ')', command=FilenameFormat)
        config_menu.configure(background = background, foreground = text_color)
        config_menu.add_separator()
        config_menu.add_command(label='Use Dark Mode (' + dark_mode + ')', command=UseDarkMode)
        config_menu.configure(background = background, foreground = text_color)
        menu_bar.add_cascade(label='Config', menu=config_menu)

        # Code for the cascading Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='Program Help  Ctrl+h', command=HelpWindow)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=AboutWindow)
        help_menu.configure(background = background, foreground = text_color)
        menu_bar.add_cascade(label='Help', menu=help_menu)

        # Top frame for the recipe name entry
        nameLabel = ttk.Label(foreground=label_text, background=label_bg, text=' Enter Recipe Title')
        self.title_frame = ttk.LabelFrame(self.frame, labelwidget=nameLabel)
        self.title_frame.grid(column=0, row=0, columnspan=2, padx=8, pady=4, sticky='W')

        # Left frame for the ingredients list
        ingLabel = ttk.Label(foreground=label_text, background=label_bg, text=' Ingreidents')
        self.ing_frame = ttk.LabelFrame(self.frame, labelwidget=ingLabel)
        self.ing_frame.grid(column=0, row=1, padx=8, pady=4, sticky = 'news')
        self.ing_frame.rowconfigure(0, weight = 1)
        self.ing_frame.columnconfigure(0, weight = 1)

        # Right frame for the directions
        dirLabel = ttk.Label(foreground=label_text, background=label_bg, text=' Directions')
        self.dir_frame = ttk.LabelFrame(self.frame, labelwidget=dirLabel)
        self.dir_frame.grid(column=1, row=1, padx=8, pady=4, sticky='nwes')
        self.dir_frame.rowconfigure(0, weight = 1)
        self.dir_frame.columnconfigure(0, weight = 1)

        # Adding a text box entry widget for the recipe title
        self.title = tk.StringVar()
        self.title_entered = tk.Entry(self.title_frame, width=75, textvariable=self.title,
                                      bd=5, relief=tk.RIDGE)
        self.title_entered.configure(background = entry_bg, foreground = entry_text, insertbackground='white')
        self.title_entered.grid(column=0, row=2, padx=8, pady=(3, 8), sticky='W')
        self.title_entered.bind("<Tab>", self.focus_next_widget)
        tt.create_ToolTip(self.title_entered, 'Enter the title of the recipe here')

        # Add a scroll box for ingredients
        self.ingredients = scrolledtext.ScrolledText(self.ing_frame, width = 30, bd=5,\
                wrap=tk.WORD, relief=tk.RIDGE)
        self.ingredients.configure(background = entry_bg, foreground = entry_text, insertbackground='white')
        self.ingredients.vbar.configure(troughcolor = scroll_color, background = scroll_bg, activebackground = scrollbar_color)
        self.ingredients.grid(column=0, row=0, padx=8, pady=(0, 20), sticky=tk.N+tk.S+tk.E+tk.W)
        self.ingredients.bind("<Tab>", self.focus_next_widget)
        tt.create_ToolTip(self.ingredients, 'Enter ingredients here, one per line\nBegin line with a period to omit bullet point')

        # Add a scroll text box for directions
        self.directions = scrolledtext.ScrolledText(self.dir_frame, bd=5,\
                wrap=tk.WORD, relief=tk.RIDGE)
        self.directions.configure(background = entry_bg, foreground = entry_text, insertbackground='white')
        self.directions.vbar.configure(troughcolor = scroll_color, background = scroll_bg, activebackground = scrollbar_color)
        self.directions.grid(column=0, row=0, padx=8, pady=(0, 20), sticky=tk.N+tk.S+tk.E+tk.W)
        self.directions.bind("<Tab>", self.focus_next_widget)
        tt.create_ToolTip(self.directions, 'Enter the recipe instructions here')

        self.title_entered.focus()  # Place cursor into the title entry box

class DefaultPath():
    '''
    Brings up the dialog box to set a default save path for use as
    a starting save location when saving a file
    '''
    def __init__(self):
        '''
        Create the new window and the two buttons to
        either select location or cancel
        '''

        path = save_path
        self.pathwin = tk.Tk()
        self.pathwin.title('Set Default Save Path')
        if path is None:
            self.current_loc = ttk.Label(self.pathwin, text = 'The current default save path is not set.')
            self.current_loc.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        else:
            self.current_loc = ttk.Label(self.pathwin, text = "The current save path is set to '{}':\n ".format(path))
            self.current_loc.grid(column=1, row=1, columnspan=2, padx=(10), pady=(15, 0), sticky='WE')
        self.msg = ttk.Label(self.pathwin, text='Click Browse to select your default save location')
        self.msg.grid(column=1, row=2, columnspan=2, padx=10, pady=(10, 25), sticky='WE')
        self.button = ttk.Button(self.pathwin, text=' Browse ', command=self.set_path)
        self.button.grid(column=1, row=3, padx=10, pady=(0, 25), sticky='WE')
        self.cancel = ttk.Button(self.pathwin, text=' Cancel ', command=self.pathwin.destroy)
        self.cancel.grid(column=2, row=3, padx=10, pady=(0, 25), sticky='WE')

    def set_path(self):
        '''
        Get the chosen location and write it to CONFIG so it is remembered
        when the program is run in the future
        '''
        path = filedialog.askdirectory()
        config.set('DefaultSavePath', 'save_path', path)
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        self.msgbox()

    def msgbox(self):
        '''
        Confirmation popup that the default path was saved
        '''
        msg.showinfo(
            'Default Save Path Set', 'Your default save \npath has been set.\n\nThis will take effect \nthe next time you run \nthe program'
            )


class SetBulletPoints():
    
    # Brings up the dialog box to set whether to use bullet points in the ingredient list

    choice = 'None'

    def __init__(self):

        # Create the popup to select the configuration setting

        self.bpwin = tk.Toplevel(root)
        self.bpwin.title('Bullet point configuration')
        if use_bp == 'True':
            self.bp_status = ttk.Label(self.bpwin, text = 'Bullet points for the ingredients is currently set to True')
            self.bp_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        else:
            self.bp_status = ttk.Label(self.bpwin, text = 'Bullet points for the ingredients is currently set to False')
            self.bp_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        self.msg = ttk.Label(self.bpwin, text = 'Select whether you want to use bullet points')
        self.msg.grid(column=1, row=2, columnspan=2, padx=10, pady=(10, 25), sticky='WE')
        self.yes = ttk.Button(self.bpwin, text = 'Yes', command=lambda:[self.bp_true(), self.bpwin.destroy()])
        self.yes.grid(column=1, row=3, padx=10, pady=(0, 25), sticky='WE')
        self.no = ttk.Button(self.bpwin, text = 'No', command=lambda:[self.bp_false(), self.bpwin.destroy()])
        self.no.grid(column=2, row=3, padx=10, pady=(0, 25), sticky='WE')
        root.eval(f'tk::PlaceWindow {str(self.bpwin)} center')

    def bp_true(self):

        # Set the use_bp setting in the CONFIG file to True

        config.set("UseBulletPoints", "use_bp", "True")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'yes'
        self.bp_msgbox(choice)

    def bp_false(self):

        # Set the use_bp setting in the CONFIG file to False

        config.set("UseBulletPoints", "use_bp", "False")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'no'
        self.bp_msgbox(choice)

    def bp_msgbox(self, choice):
        '''
        Confirmation popup that the configuration choice was saved
        '''
        if choice == 'yes':
            bp_info = tk.Toplevel(root)
            bp_info.title('Bullet point configuration set')
            message = ttk.Label(bp_info, 
                text = 'Bullet points will be used in the ingredients list\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(bp_info, text = 'Ok', command=bp_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(bp_info)} center')
        else:
            bp_info = tk.Toplevel(root)
            bp_info.title('Bullet point configuration set')
            message = ttk.Label(bp_info, 
                text = 'Bullet points will not be used in the ingredients list\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(bp_info, text = 'Ok', command=bp_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(bp_info)} center')        

class FilenameFormat():
    
    '''
    Brings up the dialog box to set whether to format the saved filenames
    Formatting will use the recipe title, converting capitals to lowercase
    and spaces to underscores.
    No formatting will use the recipe title as written for the filename.
    '''

    choice = 'None'

    def __init__(self):

        # Create the popup to select the configuration setting

        #self.fnfwin = tk.Tk()
        self.fnfwin = tk.Toplevel(root)
        self.fnfwin.title('Filename formatting configuration')
        if fn_format == 'True':
            self.fnf_status = ttk.Label(self.fnfwin, text = 'Filename formatting is currently set to True')
            self.fnf_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        else:
            self.fnf_status = ttk.Label(self.fnfwin, text = 'Filename formatting is currently set to False')
            self.fnf_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        self.msg = ttk.Label(self.fnfwin, text = 'Select whether you want to use bullet points')
        self.msg.grid(column=1, row=2, columnspan=2, padx=10, pady=(10, 25), sticky='WE')
        self.yes = ttk.Button(self.fnfwin, text = 'Yes', command=lambda:[self.fnf_true(), self.fnfwin.destroy()])
        self.yes.grid(column=1, row=3, padx=10, pady=(0, 25), sticky='WE')
        self.no = ttk.Button(self.fnfwin, text = 'No', command=lambda:[self.fnf_false(), self.fnfwin.destroy()])
        self.no.grid(column=2, row=3, padx=10, pady=(0, 25), sticky='WE')
        root.eval(f'tk::PlaceWindow {str(self.fnfwin)} center')

    def fnf_true(self):

        # Set the use_bp setting in the CONFIG file to True

        config.set("FormatFileName", "fn_format", "True")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'yes'
        self.fnf_msgbox(choice)

    def fnf_false(self):

        # Set the use_bp setting in the CONFIG file to False

        config.set("FormatFileName", "fn_format", "False")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'no'
        self.fnf_msgbox(choice)

    def fnf_msgbox(self, choice):
        '''
        Confirmation popup that the configuration choice was saved
        '''
        if choice == 'yes':
            fnf_info = tk.Toplevel(root)
            fnf_info.title('Filename formatting configuration set')
            message = ttk.Label(fnf_info, 
                text = 'Filenames will be formatted to lowercase and spaces converted to underscores\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(fnf_info, text = 'Ok', command=fnf_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(fnf_info)} center')
        else:
            fnf_info = tk.Toplevel(root)
            fnf_info.title('Filename formatting configuration set')
            message = ttk.Label(fnf_info, 
                text = 'Filenames will be the unmodified text of the recipe title\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(fnf_info, text = 'Ok', command=fnf_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(fnf_info)} center')

class UseDarkMode():

    # Brings up the dialog box to set whether to use dark mode for the application

    choice = 'None'

    def __init__(self):

        # Create the popup to select the configuration setting

        self.dmwin = tk.Toplevel(root)
        self.dmwin.title('Dark Mode configuration')
        if dark_mode == 'True':
            self.dm_status = ttk.Label(self.dmwin, text = 'You are currently using the application in Dark Mode')
            self.dm_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        else:
            self.dm_status = ttk.Label(self.dmwin, text = 'You are not currently using Dark Mode')
            self.dm_status.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        self.msg = ttk.Label(self.dmwin, text = 'Select whether you want to use Dark Mode')
        self.msg.grid(column=1, row=2, columnspan=2, padx=10, pady=(10, 25), sticky='WE')
        self.yes = ttk.Button(self.dmwin, text = 'Yes', command=lambda:[self.dm_true(), self.dmwin.destroy()])
        self.yes.grid(column=1, row=3, padx=10, pady=(0, 25), sticky='WE')
        self.no = ttk.Button(self.dmwin, text = 'No', command=lambda:[self.dm_false(), self.dmwin.destroy()])
        self.no.grid(column=2, row=3, padx=10, pady=(0, 25), sticky='WE')
        root.eval(f'tk::PlaceWindow {str(self.dmwin)} center')

    def dm_true(self):

        # Set the dark_mode setting in the CONFIG file to True

        config.set("UseDarkMode", "dark_mode", "True")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'yes'
        self.dm_msgbox(choice)

    def dm_false(self):

        # Set the dark_mode setting in the CONFIG file to False

        config.set("UseDarkMode", "dark_mode", "False")
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        choice = 'no'
        self.dm_msgbox(choice)

    def dm_msgbox(self, choice):
        '''
        Confirmation popup that the configuration choice was saved
        '''
        if choice == 'yes':
            dm_info = tk.Toplevel(root)
            dm_info.title('Dark Mode configuration set')
            message = ttk.Label(dm_info,
                text = 'You have turned Dark Mode on\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(dm_info, text = 'Ok', command=dm_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(dm_info)} center')
        else:
            dm_info = tk.Toplevel(root)
            dm_info.title('Dark Mode configuration set')
            message = ttk.Label(dm_info,
                text = 'You have turned Dark Mode off\nPlease restart the application')
            message.grid(column=1, row=1, padx=10, pady=(25, 25), sticky='WE')
            close = ttk.Button(dm_info, text = 'Ok', command=dm_info.destroy)
            close.grid(column=1, row=2, padx=10, pady=(0, 10), sticky='WE')
            root.eval(f'tk::PlaceWindow {str(dm_info)} center')

class HelpWindow():
    '''
    Pops up the window with the program usage information
    '''
    def __init__(self, master=None):
        '''
        Create the new window to hold the help text
        '''
        self.helpwin = tk.Tk()
        width = int(root.winfo_screenwidth() / 2.5)
        height = int(root.winfo_screenheight() / 1.4)
        self.helpwin.geometry('%sx%s' % (width, height))
        self.helpwin.configure(background = background)
        self.helpwin.columnconfigure(0, weight = 1)
        self.helpwin.rowconfigure(0, weight = 1)
        self.helpwin.title('Program Usage')
        self.help_text()

    def help_text(self):
        '''
        Create a scrollbox to hold the help information, open the external
        help.txt file and read the contents into the scrollbox
        vbar troughcolor is gray73, background is gray80
        button background is gray77
        '''
        
        self.help_box = scrolledtext.ScrolledText(self.helpwin,
                                                  wrap=tk.WORD, bd=5, relief=tk.RIDGE)
        self.help_box.configure(background = entry_bg, foreground = text_color)
        self.help_box.vbar.configure(troughcolor = '#bababa', background = '#cccccc')
        self.help_box.grid(column=0, row=0, padx=8, pady=(0, 20), sticky = 'nsew')
        self.help_box.insert(1.0, help_text)
        self.help_box.configure(state = 'disabled')
        self.help_button = tk.Button(self.helpwin, text='Close', command=self.helpwin.destroy)
        self.help_button.configure(foreground = text_color, background = '#c4c4c4')
        self.help_button.grid(column=0, row=1, padx=50, pady=(0, 15), sticky='we')

class AboutWindow():
    '''
    Pops up the window showing version and license info
    '''
    def __init__(self):
        '''
        Create the window to display the 'about' information
        '''
        self.aboutwin = tk.Tk()
        self.aboutwin.configure(background = background)
        self.aboutwin.title('About')
        self.about_text()

    def about_text(self):
        '''
        Create a text box to hold the about information, open the external
        file ABOUT, and read the contents into the text box
        button background is gray77
        '''
        width = 75
        height = 30
        self.about_box = tk.Text(self.aboutwin, width=width, height=height,
                                 wrap=tk.WORD, bd=5, relief=tk.RIDGE)
        self.about_box.configure(background = entry_bg, foreground = text_color)
        self.about_box.grid(column=0, row=0, padx=8, pady=(0, 20))
        self.about_box.insert(1.0, about_text)
        self.about_box.configure(state = 'disabled')
        self.about_button = tk.Button(self.aboutwin, text='Close', command=self.aboutwin.destroy)
        self.about_button.configure(foreground = text_color, background = '#c4c4c4')
        self.about_button.grid(column=0, row=1, padx=50, pady=(0, 15), sticky='WE')


#=============
#Start GUI
#=============

main = MAIN(root)    # Create an instance of the MAIN class
root.mainloop()
