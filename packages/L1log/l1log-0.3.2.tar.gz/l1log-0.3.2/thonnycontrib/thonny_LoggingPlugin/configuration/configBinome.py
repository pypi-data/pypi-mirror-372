# N'est plus utilisé pour la popup binômes, voir l1log_popups
# utilisé par MockFormatData et testFormatData.py, je ne sais pas trop à quoi ils servent.

import getpass
import tkinter as tk
import tkinter.simpledialog as simpledialog
from thonny import ui_utils


from thonny import get_workbench

from thonnycontrib.thonny_LoggingPlugin.configuration.globals import WB

user = getpass.getuser()
binome = None


def set_binome(identifiers_list:list[str]):
    """
    Affiche une fenêtre de demande de binοme et renvoie l'utilisateur de la machine ainsi que le binôme rentré.
    """
    #_BinomeDialogWindow(WB, "Qui travaille ?", user, identifiers_list)
    binome_widget = BinomeDialog(WB, user, identifiers_list)
    ui_utils.show_dialog(binome_widget)
    # en attendant d'avoir bien compris le code de Mathieu
    #_addBinomeInComments()


def get_binome():
    return user, binome


def _addBinomeInComments():
    """
    Ajoute à la création d'un fichier le nom des binômes en en-tête en commentaire.
    """
    global user, binome

    def handle_open(event):
        '''Ce code ne marche pas car en cas d'ajout d'un nom toute la ligne est recopiée. D'où le choix de Mathieu de mettre un nom par ligne ? 

        '''
        balise = "# authors identifiers :"  

        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor:
            first_line = editor.get_content().split('\n')[0]
            if first_line.startswith(balise) :
                chaine_identifiants = first_line.split(balise)[1]
                liste_identifiants = chaine_identifiants.split(' ')
                modif = False # vrai si on doit faire une modif ds l'éditeur
                if binome not in liste_identifiants :
                    liste_identifiants.insert(0, binome)
                    modif = True
                if user not in liste_identifiants :
                    liste_identifiants.insert(0, binome)
                    modif = True
                if modif :
                    new_first_line = balise + ' '.join(liste_identifiants)
                    editor.get_text_widget().insert(1.0, new_first_line + '\n')
            else:
                new_first_line = balise + ' ' + user + ' ' + binome
                editor.get_text_widget().insert(1.0, new_first_line + "\n")
    get_workbench().bind("<<NotebookTabChanged>>", handle_open, True)

# ancien code de Mathieu
    # global user, binome

    # def handle_open(event):
    #     predefined_code = "# " + user + "\n"
    #     if binome:
    #         predefined_code += "# " + binome + "\n"

    #     editor = get_workbench().get_editor_notebook().get_current_editor()
    #     if editor:
    #         first_line = editor.get_content().split('\n')[0]

    #         if not (first_line.startswith("# ") and len(first_line.split('.')) == 3):
    #             editor.get_text_widget().insert(1.0, predefined_code + "\n")

    # get_workbench().bind("<<NotebookTabChanged>>", handle_open, True)

    
class _BinomeDialogWindow(simpledialog.Dialog):
    """
    Cette classe permet d'ouvrir une fenêtre demandant les logins des binômes.
    Le premier binôme étant l'utilisateur, il est pré-rempli
    On utilise simpledialog.Dialog comme classe parent car c'est une classe qui ne demande
    pas beaucoup d'informations.
    Pour récupérer le résultat, on utilise BinomeDialogWindow.result, défini par la classe parente.
    """
    def __init__(self, parent, name, user, identifiers:list[str], essai_apres_echec:bool):
        self.user = user
        self.name_entry = None
        self.binome_name = None
        self.identifiers = identifiers
        self.essai_apres_echec = essai_apres_echec
        super().__init__(parent, name)

    def body(self, master):
        """
        creates the window, called before the user have had the chance to interact with said window,
        therefor cannot return the data by itself
        """
        # ICI
        if self.essai_apres_echec:
            tk.Label(master, text="Entrez les logins des binômes.\n").grid(row=0)
        else:
            tk.Label(master, text="Identifiant inconnu\n. Entrez les logins des binômes.\n").grid(row=0)       

        # On récupère le nom du premier binôme en récupérant le dossier utilisateur
        tk.Label(master, text="Binôme 1 : " + self.user + '').grid(row=2)
        tk.Label(master, text="Binôme 2 : ").grid(row=4)
        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=5)
        
        return self.name_entry

    def apply(self):
        """
        called when user clicks on "ok" button, retrieves and save the data
        """
        global binome
        binome = self.name_entry.get()
        if binome not in self.identifiers:
            messagebox.showinfo('Identifiant' + binome + 'inconnu', "Vérifier la saisie ou demander à votre enseignant si vous n'êtes pas inscrit")
            
        
