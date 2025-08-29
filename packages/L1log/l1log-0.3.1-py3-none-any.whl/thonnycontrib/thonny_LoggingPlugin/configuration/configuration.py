from thonnycontrib.thonny_LoggingPlugin.configuration.globals import OPTIONS, WB

from thonny.config_ui import ConfigurationPage
import tkinter as tk


def init_options():
    """
    Initialise ds le workbench les options du plugin.
    """
    for el in OPTIONS:
        if not WB.get_option(el):
            WB.set_default("loggingPlugin." + el, OPTIONS[el])


def get_option(name: str):
    """
    Renvoie la valeur ds le workbench de l'option passée en param.

    Paramètres:
    - name : le nom de l'option, tq définie ds globals.py
    """
    return WB.get_option("loggingPlugin." + name)


def accept_terms_of_uses(reponse):
    '''
    Enregistre ds le workbench le consentement de l'utilisateur.
    Param:
       - reponse(bool) : True if the user accepts, False else
    Result (None)
    '''
    WB.set_option("loggingPlugin.research_usage", reponse)


class plugin_configuration_page(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        self.add_checkbox("loggingPlugin.log_in_console", "Print logs in console")
        self.add_checkbox("loggingPlugin.store_logs", "Store logs in files")
        self.add_checkbox("loggingPlugin.research_usage", "Accept the use of user's data for research purposes")
        serv_label = tk.ttk.Label(self, text="Remote server address : (by default " + OPTIONS["server_address"] + ")")
        serv_label.grid(row=10, column=0, sticky=tk.W, pady=(5, 0), columnspan=2)
        self.add_entry("loggingPlugin.server_address", row=None, column=0, pady=10, padx=0, columnspan=1, width=100)
        folder_label = tk.ttk.Label(self, text="Local files folder : (by default " + OPTIONS["local_path"] + ")")
        folder_label.grid(row=20, column=0, sticky=tk.W, pady=(0, 0), columnspan=2)
        self.add_entry("loggingPlugin.local_path", row=None, column=0, pady=10, padx=0, columnspan=1, width=100)
