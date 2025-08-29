from thonny.shell import ShellView

import tkinter as tk
import logging
from datetime import datetime
from copy import deepcopy
import os

from thonnycontrib.thonny_LoggingPlugin.configuration import configuration
from thonnycontrib.thonny_LoggingPlugin.configuration.globals import *
from thonnycontrib.thonny_LoggingPlugin.communication.sendingClient import SendingClient
from thonnycontrib.thonny_LoggingPlugin.event.eventManager import EventManager


class EventLogger:
    """
    Main class to generate logs from user's actions
    This class bind the thonny's event generator to the function 'prepare_log'
    When an event is generated :
        Data is extracted
        Additionnal informations can be added
        The data is send to a general formatter in order to have standardised names and informations
        This data in a general format is stored, printed and next, formatted in xAPI format and sended to a server
    """

    def __init__(self, actors:tuple[str,str]):
        """
        Construct an instance of EventLogger, initiates the attributes and makes the binds to get our data
        """
        # Stockage dans la ram des logs pour les enregistrer dans un fichier lors de la fermeture de thonny
        self.thonny_logs = []           # donnée reçue de Thonny
        self.events = []                # donnée nettoyée / sélectionnée
        self.formatted_logs = []        # format intermédiaire
        self.xAPI_formatted_logs = []   # format xApi
        self.actors = actors            # binômes
        
        # Instance de la classe de formatage des event
        self.event_manager : EventManager = EventManager(self.receive_formatted_logs) # self.receive_formatted_logs = méthode qui traite l'evt une fois clôt

        # Connexion au server (si prb de connexion, il sera mis à faux)
        self.server_connection = True

        # Configs :
        self.sending_client = SendingClient(self.get_option("server_address"))
        self.research_usage = self.get_option("research_usage")
        self.log_in_console = self.get_option("log_in_console")
        self.store_logs = self.get_option("store_logs")
        self.folder = self.get_option("local_path")

        # Pour _buffer_errors
        self._stderrBuffer = dict()

        # Attribut des éléments que l'on veut séléctionner :

        self._inDict = {
            "ShellCommand": {'sequence', 'command_text', 'tags'},
            "ShellInput": {'sequence', 'input_text', 'tags'},
            "TextInsert": {'sequence', 'text', 'tags'},
            
            "Save": {'sequence', 'filename'},
            "Open": {'sequence', 'filename'},
            "SaveAs": {'sequence', 'filename'},
            
            "DebuggerResponse": {'sequence', 'stack'},

            "l1Tests": {'sequence', 'selected', 'tests', 'filename'},
            "l1Tests.DocGenerator": {'sequence', 'filename', 'signature', 'selected_lineno'}
        }

        for sequence in self._inDict:
            self._bind(sequence)
        self._bind("UiCommandDispatched")

        self.get_workbench().bind("WorkbenchClose", self._on_workbench_close, True)

        # Lance le début de Session du formater ici pour éviter problème de chargement de fichier avant début de session

        data = {
            'time' : datetime.now().isoformat(),
            'eventID' : id(self),
            'actors' : self.actors,
            'sessionID' : id(get_workbench()),
            'sequence': 'Session_start',
            'research_usage' : self.get_option('research_usage')
        }
        self._log_event(data, self)

    def _on_workbench_close(self, event: object) -> None:
        """
        write logs in files in the directory specified in the config
        """

        data = {
            'time' : datetime.now().isoformat(),
            'eventID' : id(event),
            'actors' : self.actors,
            'sessionID' : id(get_workbench()),
            'sequence': 'Session_end',
            'research_usage' : self.get_option('research_usage')
        }
        self._log_event(data, event)
        self.event_manager.flush()

        # Créer le dossier de base s'il n'existe pas
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass

        if self.store_logs:
            # Créer un dossier logs contenant tout les logs générés par le plugin
            try:
                os.mkdir(self.folder + "logs")
            except FileExistsError as e:
                pass

            import json
            time = str(datetime.now())
            time = time.split('.')[0]
            time = time.replace(' ', '_')
            time = time.replace(':', '-')
            
            
            # Thonny logs
            with open(self.folder + '/logs/thonny_logs_' + time + '.txt', encoding="UTF-8", mode="w") as fp:
                for entry in self.thonny_logs :
                    fp.write(str(entry)+"\n\n")

            # Cleaned logs
            with open(self.folder + '/logs/logs_' + time + '.json', encoding="UTF-8", mode="w") as fp:
                json.dump(self.events, fp, indent="    ")

            # intermediary logs
            with open(self.folder + '/logs/formatted_logs_' + time + '.json', encoding="UTF-8",
                      mode="w") as fp:
                json.dump(self.formatted_logs, fp, indent="    ")

            # xAPI formatted logs
            with open(self.folder + '/logs/xAPI_logs_' + time + '.json', encoding="UTF-8",
                      mode="w") as fp:
                json.dump(self.xAPI_formatted_logs, fp, indent="    ")

    def _bind(self, sequence: str) -> None:
        """
        Trigger the prepare_log function when the event type 'sequence' is produced

        Args:
            sequence (str): the event type

        Returns:
            None
        """

        def handle(event):
            self._prepare_log(sequence, event)

        self.get_workbench().bind(sequence, handle, True)

    def _prepare_log(self, sequence: str, thonny_event: object) -> None:
        """
        extract, process and log the event

        Args:
            sequence (str): the event type
            thonny_event (obj:thonny.WorkbenchEvent:) The event
        """
        if self.log_in_console:
                print('*********** Thonny statement')
                print(thonny_event)

        self.thonny_logs.append(thonny_event)

        data = self._extract_interesting_data(thonny_event, sequence) # optionnel

        data = self._input_processing(data, thonny_event)

        self._log_event(data, thonny_event)

    # TODO : thonny_event n'est pas utilisé ?
    def _log_event(self, data: dict, thonny_event: object) -> None:
        """
        Store raw data in a buffer and init an event in the formatter

        Args:
            data (obj:'dict'): the raw data
        """
        
        # Attention read_event modifie potentiellement event
        # Cas du DebuggerResponse -> del stack car stack non sérialisable
        # donc ne pas inverser ces 2 lignes
        self.event_manager.read_event(data)
        self.events.append(data)

        if self.log_in_console:
            print('*********** cleaned statement')
            print(data)

    def _extract_interesting_data(self, thonny_event, sequence):
        """
        Extract data from an Thonny's WorkbenchEvent object and select only the informations defined in the in_Dict dictionnary.

        Args :
            thonny_event (obj:thonny.WorkbenchEvent) The event to extract data from
            sequence (str) This event type

        Returns:
            (obj:'dict'): the data in the format we want
        """
        attributes = vars(thonny_event)
        data = {'tags': ()}

        for elem in self._inDict[sequence]:
            if elem in attributes:
                data[elem] = attributes[elem]
                    
        return data

    def _input_processing(self, data: dict, thonny_event: object) -> dict:
        """
        Clean and additionnal informations to the data

        Args :
            data (object:'dict') Data to process
            event

        Returns :
            data (object:'dict') Data modified
        """
        
        # Ajout contenu éditeur
        if data['sequence'] in {'ShellCommand', 'Open', 'Save', 'SaveAs', 'l1Tests'}:
            data['editorContent'] = self.get_workbench().get_editor_notebook().get_current_editor_content()
            # essai pour récup filename, parfois ça marche, parfois non...
            # editor_notebook = self.get_workbench().get_editor_notebook()
            # if editor_notebook.get_current_editor() != None:
            #      data['filename'] = editor_notebook.get_current_editor().get_long_description()
            

        data["time"] = datetime.now().isoformat()
        data['eventID'] = id(thonny_event)
        data['actors'] = self.actors
        data['sessionID'] = id(get_workbench())
        data['research_usage'] = self.get_option('research_usage')

        return data

    def _buffer_errors(self, data: dict) -> None:
        """
        Store in a buffer the data of user's text edition events and return when the user
        write somewhere else

        Args :
            data (object:'dict'): Data to process

        """
        buf = deepcopy(self._stderrBuffer)
        if buf == {}:
            self._stderrBuffer = data
        else:
            self._stderrBuffer['text'] = buf['text'] + data['text']

    def send_buffer_error(self) -> dict:
        """
        sends the error buffer
        """
        data = deepcopy(self._stderrBuffer)
        self._stderrBuffer = {}
        return data

    def receive_formatted_logs(self, formatted_log: dict) -> None:
        """
        Store and send the formatted logs in parameter to a Server if the user didn't desactivate it
        Args :
            formatted_log (object:'dict') the logs in a basic exportation format
        """
        if self.log_in_console:
                print('*********** intermediary statement')
                print(formatted_log)

        self.formatted_logs.append(formatted_log)
        xAPI_statement =  self.event_manager.parse_to_xAPI(formatted_log)
        self.xAPI_formatted_logs.append(xAPI_statement)
        try:
            if self.log_in_console:
                print('*********** xApi statement')
                print(xAPI_statement)
            self.send_xAPI_statement(xAPI_statement)
        except KeyError as e:
            logging.info(formatted_log, e)
            return

    def send_xAPI_statement(self, xAPI_statement: dict) -> None:
        """
        Send xAPI_statement to the LRS  if the user didn't desactivate it

        Args :
            data (object: dict()): dict of the data in a basic format
        """
        if self.server_connection:
            try:
                self.sending_client.send(xAPI_statement, "/statements/")
            except Exception as e:
                self.server_connection = False
                logging.warning(" Server can't be reach, restart Thonny to retry\n" + str(e))

    def get_option(self, name : str) :
        return configuration.get_option(name)

    def get_workbench(self) :
        return get_workbench()
