# definition of several popups used in L1Log

import tkinter as tk
import webbrowser

from thonny import ui_utils
from thonny.ui_utils import CommonDialog
from thonny.languages import tr
from typing import Optional

from thonny import get_workbench
from thonnycontrib.thonny_LoggingPlugin.configuration.globals import WB, URL_TERMS_OF_USE
from thonnycontrib.l1log_utils import is_joker, is_identifier_accepted

LDAP_OK = "ldap_ok"
LDAP_KO = "ldap_ko"

class AboutLoggingPlugin(CommonDialog):
    """
    Définit une pop-up avec une url d'info.
    """

    def __init__(self, master):
        import webbrowser

        super().__init__(master)

        main_frame = tk.ttk.Frame(self, width=800, height=100)
        main_frame.grid(sticky=tk.NSEW, ipadx=50, ipady=100)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        self.title("About Thonny_LoggingPLugin")

        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = tk.ttk.Label(
            main_frame, text=URL_TERMS_OF_USE, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(URL_TERMS_OF_USE))


# Mirabelle
# inspiré de thonny.ui_utils.QueryDialog, certaines choses sont
# peut-être inutiles.
class ConsentementDialog(ui_utils.CommonDialogEx):
    """
    Définition d'une pop-up lancée au premier démarrage de Thonny
    qui demande si l'utilisateur consent à ce qu'on collecte
    ses données.
    Si la fenêtre est fermée sans avoir cliqué oui ou non,
    l'absence de réponse est interprétée comme "non".
    """

    def __init__(
            self,
            master,
            entry_width: Optional[int] = None,
    ):
        super().__init__(master)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # question posée
        self.question = "Acceptez vous que les données utilisateur issues de Thonny soient utilisées\n à des fins de recherche ?"
        bold_font = tk.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight=tk.font.BOLD)
        # autres textes à afficher ds la pop-up
        self.prompt1 = "Les données seront pseudo-anonymisées. Les commentaires et noms de fichier seront supprimés\n car pouvant " \
                       "contenir des données personnelles (nom, prénom, groupe).\n Attention à ne pas faire figurer " \
                       "de données personnelles dans le reste du code."
        # autres textes à afficher ds la pop-up
        # self.prompt1 = "Les commentaires en tête de fichier et le nom du fichier ne sont pas collectés\n car pouvant " \
        #                "contenir des données personnelles (nom, prénom, groupe).\n Attention à ne pas faire figurer " \
        #                "de données personnelles dans le reste du code."
        self.prompt2 = "Vous pourrez modifier votre choix à tout moment dans le menu outils-->options, onglet LoggingPlugin"
        self.mention_legale_courte1 = "Les informations recueillies sont enregistrées dans un fichier informatisé " \
                                      "par CRIStAL. Ces données font l'objet\nd'un traitement informatique destiné " \
                                      "à la collecte automatique des traces numériques laissées par les\napprenant·es" \
                                      " dans l’environnement de programmation Thonny et à leur pseudo-anonymisation. Les " \
                                      "destinataires des\ndonnées sont les membres de l'équipe de recherche Noce." \
                                      "\n\nToute personne peut obtenir communication et, le cas échéant, " \
                                      "rectification ou suppression des informations\nla concernant, en s'adressant " \
                                      "aux responsables du projet (contact-l1log@univ-lille.fr). Pour toute autre " \
                                      "question,\nvous avez la possibilité de contacter notre délégué à la " \
                                      "protection des données."
        self.dpo = "https://www.cristal.univ-lille.fr/contact?categorie=rgpd"
        self.prompt3 = "Informations détaillées sur la collecte ici"
        # résultat issu de la pop-up : None, "oui", "non"
        self.result = None

        # ???
        margin = self.get_large_padding()
        spacing = margin // 2

        # titre de la pop-up
        self.title("Conditions d'utilisation")

        # positionnement question + annonces
        self.prompt_question = tk.ttk.Label(self.main_frame, text=self.question, font=bold_font)
        self.prompt_question.grid(row=1, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        self.prompt_label1 = tk.ttk.Label(self.main_frame, text=self.prompt1)
        self.prompt_label1.grid(row=2, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        self.prompt_label2 = tk.ttk.Label(self.main_frame, text=self.prompt2)
        self.prompt_label2.grid(row=3, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        self.prompt_label3 = tk.ttk.Label(self.main_frame, text=self.prompt3, style="Url.TLabel", font=url_font)
        self.prompt_label3.grid(row=4, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        self.prompt_label3.bind("<Button-1>", lambda _: webbrowser.open(URL_TERMS_OF_USE))

        # je place le bouton "non" en premier pour qu'il ait le focus
        # par défaut. J'ai essayé focus_set sans aucun effet.
        # Je ne comprends pas...
        # self.non_button.focus_set()

        # bouton non
        self.non_button = tk.ttk.Button(
            self.main_frame, text=tr("non"), command=self.on_non, default="active")
        self.non_button.grid(row=6, column=1, padx=(margin, spacing), pady=(0, margin))

        # bouton oui
        self.oui_button = tk.ttk.Button(
            self.main_frame, text=tr("oui"), command=self.on_oui, default="active")
        self.oui_button.grid(row=5, column=1, padx=(margin, spacing), pady=(0, margin))

        # mention légale
        self.prompt_mention_legale1 = tk.ttk.Label(self.main_frame, text=self.mention_legale_courte1, font=(None, 8))
        self.prompt_mention_legale1.grid(row=7, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label2 = tk.ttk.Label(
            self.main_frame, text=self.dpo, style="Url.TLabel", cursor="hand2", font=(url_font, 8)
        )
        url_label2.grid(row=8, column=1, columnspan=2, padx=margin, pady=(margin, spacing))
        url_label2.bind("<Button-1>", lambda _: webbrowser.open(self.dpo))

        # ???
        self.main_frame.columnconfigure(1, weight=1)

    def on_oui(self, event=None):
        self.result = "oui"
        self.destroy()

    def on_non(self, event=None):
        self.result = "non"
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[str]:
        '''
        Renvoie :
        - "oui" si click sur le bouton "oui"
        - "non" si click sur le bouton "non"
        - None si fermeture fenêtre sans click
        '''
        return self.result

class BinomeDialog(ui_utils.CommonDialogEx):

    def __init__(self, parent, user, ldap_identifiers:list[str], mode:str):
        self.user = user # identifier of connected student
        self.mode = mode # nominal mode : LDAP_OK or backup mode : LDAP_KO
        self.binome_name = None
        self.identifiers = ldap_identifiers # MI identifiers from ldap
        super().__init__(parent)
        self.parent = parent

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        margin = self.get_large_padding()
        spacing = margin // 2
        self.title("Qui travaille ?")

        bold_font = tk.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight=tk.font.BOLD)

        tk.Label(self.main_frame, text="Étudiant·e connecté·e : " + self.user + '').pack(anchor=tk.N, pady=20)
        
        if self.mode == LDAP_OK:
            self.message3 = "\t * en binôme : entrer son identidiant prenom.nom.etu"
        elif self.mode == LDAP_KO:
            self.message_no_ldap = " Impossible de vérifier l'identifiant de la 2ème personne qui travaille."
            self.prompt = tk.ttk.Label(self.main_frame, text=self.message_no_ldap)
            self.prompt.pack(anchor=tk.N, pady=20)
            self.message3 = "\t * en binôme : entrer un joker fourni par l'enseignant·e"
        self.message2 = "Si " + self.user + " travaille... \n \t * seul·e : laisser le champ vide"
        self.prompt2 = tk.ttk.Label(self.main_frame, text=self.message2, font=bold_font)
        self.prompt2.pack(anchor=tk.W)            

        self.prompt3 = tk.ttk.Label(self.main_frame, text=self.message3, font=bold_font)
        self.prompt3.pack(anchor=tk.W)
        self.message4 = "... puis cliquer sur OK"
        self.prompt4 = tk.ttk.Label(self.main_frame, text=self.message4, font=bold_font)
        self.prompt4.pack(anchor=tk.W, pady=10)
        
        self.identifier_entry = tk.ttk.Entry(self.main_frame, width=50)
        self.identifier_entry.pack(anchor=tk.S, pady=20)
        self.identifier_entry.bind("<Return>", self.on_ok)

        self.ok_button = tk.ttk.Button(self.main_frame, text='OK', command=self.on_ok)
        self.ok_button.pack(anchor=tk.S, pady=20)

    def on_ok(self, event = None):
        bold_font = tk.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight=tk.font.BOLD)

        self.binome_name = self.identifier_entry.get()
        if is_identifier_accepted(self.binome_name, self.identifiers):
            self.destroy()
        else:
            self.warning_msg1 = 'Identifiant ' + self.binome_name + ' inconnu.\n'
            self.binome_name = ''
            if self.mode == LDAP_OK: 
                self.warning_msg2 = "Vérifier et modifier la saisie ou demander à votre enseignant·e un joker si le.a binôme n'est pas inscrit·e...\n \t puis cliquer sur OK."
            elif self.mode == LDAP_KO:
                self.warning_msg2 = "Vérifier et modifier la saisie du joker....\n \t puis cliquer sur OK."
            self.prompt = tk.ttk.Label(self.main_frame, text=self.warning_msg1, font=bold_font)
            self.prompt.pack(anchor=tk.N, pady=10)
            self.prompt2 = tk.ttk.Label(self.main_frame, text=self.warning_msg2, font=bold_font)
            self.prompt2.pack(anchor=tk.N)

    def on_cancel(self, event=None):
        if self.parent:
            self.binome_name = ''
            self.destroy()
        else:
            sys.exit('fermeture de la fenêtre principale de Thonny')

            
    def get_second_identifier(self)-> str:
        return self.binome_name

def display_about_plugin() -> None:
    """
    Affiche une pop-up avec une url.
    """
    ui_utils.show_dialog(AboutLoggingPlugin(WB))


def display_terms_of_use() -> str:
    """
    Ouvre la fenêtre de consentement. Renvoie True si l'utilisateur
    est d'accord pour la collecte de ses données.

    Result:
       (bool) vrai si l'utilisateur a cliqué sur "oui", faux
       pour toute autre interaction.
    """
    fenetre_consentement = ConsentementDialog(WB)
    ui_utils.show_dialog(fenetre_consentement)
    reponse = fenetre_consentement.get_result()
    return reponse == "oui"


def display_binome_request(user1:str, identifiers:list[str], mode:str) -> tuple[str, str]:
    '''
    Asks the name of student2 and returns (user1, student2).
    If the name is not in identifiers, ask again. 
    
    Args:
    - user1 : identifier of the connected student
    - identifiers: list of MI student identifiers
    - mode : LDAP_OK or LDAP_KO
    '''
    binome_widget = BinomeDialog(WB, user1, identifiers, mode)
    ui_utils.show_dialog(binome_widget)
    user2 = binome_widget.get_second_identifier()
    return (user1, user2)

# ancien code Mathieu, à reprendre un jour...
# def _addBinomeInComments():
#     """
#     Ajoute à la création d'un fichier le nom des binômes en en-tête en commentaire.
#     """
#     global user, binome

#     def handle_open(event):
#         '''Ce code ne marche pas car en cas d'ajout d'un nom toute la ligne est recopiée. D'où le choix de Mathieu de mettre un nom par ligne ? 

#         '''
#         balise = "# authors identifiers :"  

#         editor = get_workbench().get_editor_notebook().get_current_editor()
#         if editor:
#             first_line = editor.get_content().split('\n')[0]
#             if first_line.startswith(balise) :
#                 chaine_identifiants = first_line.split(balise)[1]
#                 liste_identifiants = chaine_identifiants.split(' ')
#                 modif = False # vrai si on doit faire une modif ds l'éditeur
#                 if binome not in liste_identifiants :
#                     liste_identifiants.insert(0, binome)
#                     modif = True
#                 if user not in liste_identifiants :
#                     liste_identifiants.insert(0, binome)
#                     modif = True
#                 if modif :
#                     new_first_line = balise + ' '.join(liste_identifiants)
#                     editor.get_text_widget().insert(1.0, new_first_line + '\n')
#             else:
#                 new_first_line = balise + ' ' + user + ' ' + binome
#                 editor.get_text_widget().insert(1.0, new_first_line + "\n")
#     get_workbench().bind("<<NotebookTabChanged>>", handle_open, True)

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
