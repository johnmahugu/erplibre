#! /usr/bin/python
# -*- coding: utf-8 -*-

#    This is a Python open source project for migration of modules
#    and functions from GestionPyme and other ERP products from Sistemas
#    Ágiles.
#
#   Copyright (C) 2012 Sistemas Ágiles.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Alan Etkin <spametki@gmail.com>"
__copyright__ = "Copyright (C) 2012 Sistemas Ágiles"
__license__ = "AGPLv3"

HELP_TEXT = """
    WARNING: This is not a Distutils installation script.
    
    The naming convention is only used for the installer to
    make it easily found and run. This script will copy the source
    modules and other files to the user defined target, without
    building any file to the Python packages or performing Python
    environment configurations.
    
    ERP Libre setup command options:

    ./setup.py [option 1 [value 1]] ... [option n]

    * --help : Display this text
    * --?: same as help
    
    * --install : Start server/client configuration. It asks for
    the web2py/gui2py folders, db URI, and wether it must install
    the webapp in the current web2py installation. Writes the
    config.ini file with the installation basic parameters

    * --hmac_key [value] : special key for the web2py auth class (use a local
    key for each ERP Libre project. Use the same key for client
    installations). If not specified, it is configured during
    installation. (used with --install)

    * --client : Configure as client gui application (used with
    --install)

    * --dep [true/false]: Install dependencies (if true, the script will
    ask confirmation for each library installation). Defaults to true

    * --web2py_app [true/false]: Install the web2py application
    (used with --install). Defaults to true
    
    * --gui [true/false]: Use graphical dialogs on installation. Displays
    the installation options in the terminal (used with --install).
    Defaults to true
    
    * --web2py_path [value] : Absolute path to the local web2py installation
    (used with --install)
    
    * --gui2py_path [value] : Absolute path to the local gui2py installation
    (used with --install)
"""

import sys, os, random
import tarfile
import zipfile
    
try:
    import readline
except ImportError:
    print "readline feature not supported for user input"

try:
    import wx
    from modules import setup_gui
    MyFrame = setup_gui.MyFrame
    GUI = True
except ImportError:
    print "wxPython not found. You cannot run the desktop app without wx."
    GUI = False

# Look for the web2py and gui2py installers

CWD = os.getcwd()
os.chdir("../")
ONE_LEVEL_UP = os.getcwd()
os.chdir(CWD)

PRIVATE_FOLDER = os.path.join(CWD, "private")
WEB2PY_INSTALLER = None
GUI2PY_INSTALLER = None

for filename in os.listdir(PRIVATE_FOLDER):
    name = filename.upper()
    isinstallfile = False
    if name.endswith(".WP2") or name.endswith(".ZIP"): isinstallfile = True
    if isinstallfile:
        if "WEB2PY" in name and isinstallfile:
            WEB2PY_INSTALLER = os.path.join(PRIVATE_FOLDER, filename)
        elif "GUI2PY" in filename.upper():
            GUI2PY_INSTALLER = os.path.join(PRIVATE_FOLDER, filename)

WEB2PY_APP = True
PATH_WALK = None
GUI2PY_PATH = None
WEB2PY_PATH = None
CLIENT = False
LEGACY_DB = False
HMAC_KEY = None
LANGUAGE = ""
DEP = True

def create_dirs():
    print "Creating subfolders... "
    for subfolder in ["databases",]:
        path = os.path.join(CWD, subfolder)
        if not os.path.exists(path):
            os.mkdir(path)
    return None

def create_hmac_key():
    # a naive hmac key creator
    # TODO: implement web2py automated hmac keys
    hmk="sha512:3f00b793-28b8-4b3c-8ffb-081b57fac54a"
    new_hmac_key = "sha512:"
    for i, c in enumerate(hmk):
        if i > 6:
            if c != "-":
                new_hmac_key += random.choice(tuple("0123456789abcdef"))
            else:
                new_hmac_key += c
    return new_hmac_key

def extract(filename, path):
    print "filename", filename
    print "path", path
    print "Extracting %s to %s" % (filename, path)
    if filename.upper().endswith(".W2P"):
        tf = tarfile.open(filename)
        tf.extractall(path=path)
        tf.close()
        print "done"
    elif filename.upper().endswith(".ZIP"):
        zf = zipfile.ZipFile(filename, 'r')
        zf.extractall(path)
        zf.close()
        print "done"
    else:
        print "Could not extract the installer: extension must be .w2p or .zip"

def set_values(web2py_path, gui2py_path, gui = GUI, \
client = CLIENT, legacy_db = LEGACY_DB, hmac_key = HMAC_KEY, \
language = LANGUAGE, web2py_app = WEB2PY_APP):
    
    try:
        login = os.getlogin()
    except (AttributeError, OSError):
        login = ""

    WEB2PY_PATH = web2py_path
    GUI2PY_PATH = gui2py_path

    if not web2py_app:
        web2py_app_folder = ""
    else:
        web2py_app_folder = os.path.join(WEB2PY_PATH, \
        "applications", WEB2PY_APP_NAME)

    # set default paths (templates, example_db, ...)

    ini_values = dict(APP_NAME = APP_NAME,
    SYSTEM_USER_NAME = login,
    GUI2PY_APP_FOLDER = CWD,
    GUI2PY_APP_CLIENT = client,
    WEB2PY_APP_NAME = WEB2PY_APP_NAME,
    WEB2PY_FOLDER = WEB2PY_PATH,
    GUI2PY_FOLDER = GUI2PY_PATH,
    WEB2PY_APP_FOLDER = web2py_app_folder,
    DATABASES_FOLDER = os.path.join(CWD, "databases"),
    TEMPLATES_FOLDER = os.path.join(CWD, "views"),
    PDF_TEMPLATES_FOLDER = os.path.join(CWD, "pdf_templates"),
    OUTPUT_FOLDER = os.path.join(CWD, "output"),
    DB_URI = r'sqlite://storage.sqlite',
    DB_TIMEOUT = -1,
    HMAC_KEY = hmac_key,
    LEGACY_DB = legacy_db,
    LANGUAGE = language)

    # confirm db_uri or change it interactively

    # present a modal widget with connection string confirmation
    confirm_text = "Please confirm db connection string %s" % ini_values["DB_URI"]
    
    if gui:
        retCode = wx.MessageBox(confirm_text, "db URI String", wx.YES_NO | wx.ICON_QUESTION)
        if retCode == wx.YES:
            confirm_uri_string = "y"
        else:
            confirm_uri_string = "n"
    else:
        confirm_uri_string = raw_input(confirm_text + " (y/n):")

    if not confirm_uri_string in ("\n", "Y", "y", None, ""):
        # if change uri is requested
        # prompt for uri
        
        prompt_for_db_uri = "Type a valid web2py db connection URI and press Enter"
        
        if gui:
            new_uri_string = wx.GetTextFromUser(prompt_for_db_uri, caption="Input text", default_value=ini_values["DB_URI"], parent=None)
        else:
            new_uri_string = raw_input(prompt_for_db_uri + " :")
            
        ini_values["DB_URI"] = str(new_uri_string)
        if ini_values["DB_URI"] in ("", None):
            print "Installation cancelled. Db conection string was not specified"
            exit(1)

    demo_key = "sha512:3f00b793-28b8-4b3c-8ffb-081b57fac54a"
    
    if hmac_key is None:
        confirm_text = "Do you want to keep the demo hmac key? %s :" % demo_key
        
        if gui:
            retCode = wx.MessageBox(confirm_text, "HMAC KEY", wx.YES_NO | wx.ICON_QUESTION)
            if retCode == wx.YES:
                confirm_hmac = "y"
            else:
                confirm_hmac = "n"
        else:
            confirm_hmac = raw_input(confirm_text + " (y/n):")

        if not confirm_hmac.strip() in ("\n", "Y", "y", None, ""):
            # if change hmac is requested
            # prompt for hmac

            prompt_for_hmac = "You can use the random key, type a custom key or type \"new\" to retry"

            user_input_loop = True
            while user_input_loop == True:
                new_random_key=create_hmac_key()
                if gui:
                    new_hmac = wx.GetTextFromUser(prompt_for_hmac, caption="Input text", default_value=new_random_key, parent=None)
                else:
                    new_hmac = raw_input(prompt_for_hmac + " " + new_random_key + " (Enter):").strip()
                    
                if new_hmac == "new":
                    # new key requested
                    continue
                elif new_hmac in (None, ""):
                    if not gui:
                        # terminal input accepts the random key
                        ini_values["HMAC_KEY"] = new_random_key
                        user_input_loop = False
                    else:
                        print "Installation cancelled. hmac key was not specified"
                        exit(1)
                else:
                    # store wathever was entered
                    ini_values["HMAC_KEY"] = new_hmac
                    user_input_loop = False

        else:
            # demo key
            ini_values["HMAC_KEY"] = demo_key

    # write config values to config.ini
    print "Writing config values to config.ini"

    with open("config.ini", "wb") as config:
        for k, v in ini_values.iteritems():
            config.write(k + "=" + str(v) + "\n")

    # write config values to config.ini
    # for path search purposes mostly
    if WEB2PY_APP:
        print "Writing config values to web2py app"
        if ini_values["WEB2PY_APP_FOLDER"] != "":
            # TODO: and ...FOLDER has a valid path
            with open(os.path.join(ini_values["WEB2PY_APP_FOLDER"], "private", "config.ini"), "wb") as config:
                for k, v in ini_values.iteritems():
                    config.write(k + "=" + str(v) + "\n")

    # exit with status 0 and message
    print "Installation finished."
    print "You can run ERP Libre from %s with >python main.py" \
    % CWD
    
    return True


def start_install(evt):
    global GUI2PY_PATH
    global WEB2PY_PATH
    global ONE_LEVEL_UP

    # Install dependencies?
    if DEP:
        # set status bar text with message "web2py path"
        starting_frame.SetStatusText( \
        "web2py installation target")

        if WEB2PY_PATH is None:
            ddlg_web2py = wx.MessageDialog(None, \
            "Do you want to install web2py? Choose 'no' to provide web2py location",
                    'web2py installation', wx.YES | wx.NO)

            install_web2py = ddlg_web2py.ShowModal()

            wx.MessageDialog(None, \
            "Select web2py installation folder",
                    'web2py installation folder', wx.OK).ShowModal()
            ddlg_web2py_target = wx.DirDialog(starting_frame, \
            message="web2py installation target", defaultPath=ONE_LEVEL_UP)
            path_choice = ddlg_web2py_target.ShowModal()

            if path_choice == wx.ID_CANCEL:
                print "No path specified for web2py. Installation failed."
                exit(1)
                
            web2py_target = ddlg_web2py_target.GetPath()

            if not web2py_target in ["", None]:
                if install_web2py == wx.ID_YES:
                    starting_frame.SetStatusText( \
                    "now copying web2py")
                    extract(WEB2PY_INSTALLER, web2py_target)
                    WEB2PY_PATH = os.path.join(web2py_target, "web2py")
                else:
                    WEB2PY_PATH = web2py_target
            else:
                print "No path specified for web2py. Installation failed."
                exit(1)

        # set status bar text with message "gui2py path"
        starting_frame.SetStatusText( \
        "gui2py installation target")

        if GUI2PY_PATH is None:
            ddlg_gui2py = wx.MessageDialog(None, \
            "Do you want to install gui2py? Choose 'no' to provide gui2py location",
                    'gui2py installation', wx.YES | wx.NO)

            install_gui2py = ddlg_gui2py.ShowModal()

            wx.MessageDialog(None, \
            "Select a gui2py installation folder",
                    'gui2py installation folder', wx.OK).ShowModal()

            ddlg_gui2py_target = wx.DirDialog(starting_frame, \
            message="gui2py installation target", defaultPath=ONE_LEVEL_UP)
            path_choice = ddlg_gui2py_target.ShowModal()
            if path_choice == wx.ID_CANCEL:
                print "No path specified for gui2py. Installation failed."
                exit(1)

            gui2py_target = ddlg_gui2py_target.GetPath()

            if not gui2py_target in ["", None]:
                if install_gui2py == wx.ID_YES:
                    starting_frame.SetStatusText( \
                    "now copying gui2py")
                    extract(GUI2PY_INSTALLER, gui2py_target)
                    GUI2PY_PATH = os.path.join(gui2py_target, "gui2py")
                else:
                    GUI2PY_PATH = gui2py_target
            else:
                print "No path specified for gui2py. Installation failed."
                exit(1)

    else:
        if WEB2PY_PATH in ("", None):
            # Ask the user for web2py and gui2py paths
            # set status bar text with message "web2py path"
            starting_frame.SetStatusText( \
            "web2py installation path")

            wx.MessageDialog(None, \
            "Please specify your web2py installation folder",
                    'web2py folder', wx.OK).ShowModal()

            ddlg_web2py = wx.DirDialog(starting_frame, \
            message="web2py installation path", defaultPath=CWD)

            searching = True
            while searching == True:
                if ddlg_web2py.ShowModal() == wx.ID_OK:
                    # assign path to WEB2PY_PATH
                    starting_frame.SetStatusText(\
                    "web2py path set to " + ddlg_web2py.GetPath())

                    WEB2PY_PATH = ddlg_web2py.GetPath()

                    starting_frame.gauge.SetValue(10)
                    break

                else:
                    # action cancelled
                    # show modal dialog for exit

                    dlg = wx.MessageDialog(None, \
                    "Do you want to continue (you must specify web2py path first)?",
                    'Re-enter web2py path', wx.YES_NO | wx.ICON_QUESTION)
                    retCode = dlg.ShowModal()

                    if (retCode == wx.ID_YES):
                        dlg.Destroy()
                        continue
                    else:
                        print "Installation cancelled by user input"
                        dlg.Destroy()
                        searching = False
                        starting_frame.Close()
                        ERPLibreSetup.Exit()
                        exit(1)
                        
        if GUI2PY_PATH in (None, ""):
            # set status bar text with message "gui2py path"
            starting_frame.SetStatusText("gui2py installation path")

            wx.MessageDialog(None, \
            "Please specify your gui2py installation folder",
                    'gui2py path', wx.OK).ShowModal()

            ddlg_gui2py = wx.DirDialog(starting_frame, \
            message="gui2py installation path", defaultPath=CWD)

            searching = True

            while searching == True:
                if ddlg_gui2py.ShowModal() == wx.ID_OK:
                    # assign path to GUI2PY_PATH
                    starting_frame.SetStatusText("gui2py path set to " \
                    + ddlg_gui2py.GetPath())
                    GUI2PY_PATH = ddlg_gui2py.GetPath()
                    starting_frame.gauge.SetValue(20)
                    break

                else:
                    # action cancelled
                    # show modal dialog for exit

                    dlg = wx.MessageDialog(None, \
                    "Do you want to continue (you must specify gui2py path first)?",
                    'Re-enter gui2py path', wx.YES_NO | wx.ICON_QUESTION)
                    retCode = dlg.ShowModal()
                    if (retCode == wx.ID_YES):
                        dlg.Destroy()
                        continue
                    else:
                        print "Installation cancelled by user input"
                        dlg.Destroy()
                        searching = False
                        starting_frame.Close()
                        ERPLibreSetup.Exit()
                        exit(1)

    if WEB2PY_APP:
        starting_frame.SetStatusText( \
        "web2py app installation")
        
        if (WEB2PY_PATH is not None):
            dlg = wx.MessageDialog(None, \
            "Confirm web2py app installation at %s?" \
            % os.path.join(WEB2PY_PATH, "applications", \
            WEB2PY_APP_NAME),
            'Confirm web2pyapp installation', \
            wx.YES_NO | wx.ICON_QUESTION)
            retCode = dlg.ShowModal()
            if (retCode == wx.ID_YES):
                dlg.Destroy()

            else:
                print "Could not install web2pyapp. Installation cancelled"
                dlg.Destroy()
                searching = False
                starting_frame.Close()
                ERPLibreSetup.Exit()
                exit(1)

            print "Writing web2py app to disk"
            starting_frame.SetStatusText( \
            "now copying the web2py app")

            extract(os.path.join(PRIVATE_FOLDER,
                                 "web2py.app.erplibre.w2p"),
                    os.path.join(WEB2PY_PATH, "applications",
                                 WEB2PY_APP_NAME))

            starting_frame.gauge.SetValue(40)
            starting_frame.SetStatusText( \
            "web2py app installation complete. Please restart web2py server")

        else:
            print "Installation cancelled. Could not copy web2py app files."
            exit(1)

    create_dirs()
    result = set_values(WEB2PY_PATH, GUI2PY_PATH, gui = GUI, \
    client = CLIENT, legacy_db = LEGACY_DB, web2py_app = WEB2PY_APP)

    if result == True:
        starting_frame.gauge.SetValue(50)
        starting_frame.SetStatusText( \
        "Setup complete")
        starting_frame.button_start.Enable(False)

        wx.MessageDialog(None, \
    u"Setup completed successfully", "Setup complete", wx.OK).ShowModal()


def search_folder_path(name):
    global PATH_WALK
    if PATH_WALK is None:
        PATH_WALK = os.walk("/")

    search_loop = True

    print "Searching for %s path. Please wait." % name
    
    while search_loop:
        try:
            path_info = PATH_WALK.next()
            if name in os.path.basename(path_info[0]) and os.path.isdir(path_info[0]):
                path = path_info[0]
                if not path in paths:
                    paths.append(path_info[0])

        except StopIteration:
            # end of walk reached
            search_loop = False
    return None


command_args = [arg.upper().replace("-", "") for arg in sys.argv]

if "HELP" in command_args or "?" in command_args:
    print HELP_TEXT
    exit(0)

elif "INSTALL" in command_args:
    paths = []
    PATH_WALK = None
    WEB2PY_PATH = None
    GUI2PY_PATH = None

    APP_NAME = "erplibre"
    WEB2PY_APP_NAME = "erplibre"

    arg_counter = 0

    for arg in sys.argv:
        upper_arg = arg.upper()
        arg_name = upper_arg.replace("-", "")

        arg_counter += 1

        if arg_name == "GUI":
            if sys.argv[arg_counter].upper() in ["N", "NO", "F", "FALSE"]:
                GUI = False
                print "No gui mode"

        elif arg_name == "WEB2PY_APP":
            if sys.argv[arg_counter].upper() in ["N", "NO", "F", "FALSE"]:
                WEB2PY_APP = False
                print "web2py app installation disabled"

        elif arg_name == "WEB2PY_PATH":
            WEB2PY_PATH = sys.argv[arg_counter]

        elif arg_name == "GUI2PY_PATH":
            GUI2PY_PATH = sys.argv[arg_counter]

        elif arg_name == "WEB2PY_APP_NAME":
            WEB2PY_APP_NAME = sys.argv[arg_counter]

        elif arg_name == "LANGUAGE":
            LANGUAGE = sys.argv[arg_counter]

        elif arg_name == "APP_NAME":
            APP_NAME = sys.argv[arg_counter]

        elif arg_name == "CLIENT":
            CLIENT = True
            WEB2PY_APP = False

        elif arg_name == "LEGACY_DB":
            LEGACY_DB = True

        elif arg_name == "HMAC_KEY":
            HMAC_KEY = sys.argv[arg_counter]

        elif arg_name == "DEP":
            if sys.argv[arg_counter].upper() in ["N", "NO", "F", "FALSE"]:
                print "Skip dependencies"
                DEP = False

    if GUI:
        # start Setup wx window
        ERPLibreSetup = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        starting_frame = MyFrame(None, -1, "")
        starting_frame.SetSize((640, 360))
        ERPLibreSetup.SetTopWindow(starting_frame)
        starting_frame.Bind(wx.EVT_BUTTON, start_install, starting_frame.button_start)
        starting_frame.SetStatusText("ERP Libre installation utility. Press Install to start")
        starting_frame.Show()
        ERPLibreSetup.MainLoop()


    else:
        # Installation without wxPython Dialogs
        # Install dependencies?
        if DEP:
            if WEB2PY_PATH is None:
                web2py_target = ONE_LEVEL_UP
                web2py_target = raw_input("Press Enter to install web2py to %s or type a new path. Type N for no installation:" % web2py_target)
                if web2py_target == "": web2py_target = ONE_LEVEL_UP
                if web2py_target.upper() != ("N"):
                    extract(WEB2PY_INSTALLER, web2py_target)
                    WEB2PY_PATH = os.path.join(web2py_target, "web2py")

            if GUI2PY_PATH is None:
                gui2py_target = ONE_LEVEL_UP
                gui2py_target = raw_input("Press Enter to install gui2py to %s or type a new path. Type N for no installation:" % gui2py_target)
                if gui2py_target == "": gui2py_target = ONE_LEVEL_UP
                if gui2py_target.upper() != "N":
                    extract(GUI2PY_INSTALLER, gui2py_target)
                    GUI2PY_PATH = os.path.join(gui2py_target, "gui2py")

        if WEB2PY_PATH in [None, "N"]:
            # Search path for web2py installation

            # reset os path walk
            PATH_WALK = None
            the_folder = None
            paths = []

            feedback = raw_input("Please specify the absolute path to your web2py installation or press Enter for auto search (it might take a while):")
            if feedback:
                WEB2PY_PATH = feedback
            else:
                # Loop trough each folder named web2py in system
                # create paths options

                search_folder_path("web2py")
                options = []

                if len(paths) > 0:
                    print
                    print "Select a path for your actual web2py installation:"
                    print "###################################################"

                    for i, option in enumerate(paths):
                        options.append(i)
                        print option, " [%s]" % i
                    print

                    try:
                        choice = int(raw_input("Choose a path index:"))
                        WEB2PY_PATH = paths[choice]
                    except (TypeError, IndexError):
                        print "You chosed an invalid path index"
                        exit(1)
                else:
                    print """
                    Could not find the path for web2py.
                    Please install it or set the path manually with
                    > python setup.py install --WEB2PY_PATH [path]
                    """
                    exit(1)

        # If web2py applications folder found, request write confirmation.
        if WEB2PY_APP:
            if raw_input(\
            "Please confirm ERP Libre App installation at %s (y/n):" \
            % os.path.join(WEB2PY_PATH, "applications", WEB2PY_APP_NAME)) in ["y", "Y"]:
                # If write confirmation,
                # copy web2py.app.erplibre.w2p files
                # to web2py applications folder
                print "Writing web2py app to disk"
                extract(os.path.join(PRIVATE_FOLDER,
                                 "web2py.app.erplibre.w2p"),
                        os.path.join(WEB2PY_PATH,
                                     "applications",
                                      WEB2PY_APP_NAME))
                print "App installation complete. Please restart web2py"
            else:
                print "Installation cancelled. Could not copy web2py app files."
                exit(1)

        # Loop trough each folder named gui2py in system
        # If gui2py folder found. request confirmation.
        # If confirmation, set the gui2py folder
        # If no confirmation, continue loop
        # if no gui2py folder found, exit with error 1

        if GUI2PY_PATH in ["N", None]:
            # Search path for gui2py installation
            # reset os path walk
            PATH_WALK = None
            the_folder = None
            paths = []

            feedback = raw_input("Please specify the absolute path to your gui2py installation or press Enter for auto search (it might take a while):")

            if feedback:
                GUI2PY_PATH = feedback
            else:
                options = []
                search_folder_path("gui2py")

                if len(paths) > 0:
                    print
                    print "Select a path for your actual gui2py installation:"
                    print "###################################################"

                    for i, option in enumerate(paths):
                        options.append(i)
                        print option, " [%s]" % i
                    print

                    try:
                        choice = int(raw_input("Choose a path index:"))
                        GUI2PY_PATH = paths[choice]
                    except (TypeError, IndexError):
                        print "You chosed an invalid path index"
                        exit(1)
                else:
                    print """
                    Could not find the path for gui2py.
                    Please install it or set the path manually with
                    > python setup.py install --GUI2PY_PATH [path]
                    """
                    exit(1)
                    
        create_dirs()
        result = set_values(WEB2PY_PATH, GUI2PY_PATH, gui = GUI, \
        client = CLIENT, legacy_db = LEGACY_DB, web2py_app = WEB2PY_APP)
        
        if result == True:
            exit(0)
        else:
            exit(1)

else:
    print "Run python setup.py --install for initial setup"
    exit(0)

