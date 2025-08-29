from .eventFactory import EventFactory
from .event import Event

class EventManager() :
    """
    The EventManager read data for any event and use the rigth event class to format them.
    """

    def __init__(self, return_created_data) :
        """
        Initialize the class EventManager.

        Args:
            return_created_data (obj:'def(dict)'): The function to call back to return the data of event when flush.
        """

        self.factory : EventFactory = EventFactory()
        self.currentEvent : Event = self.factory.create_event(None, return_created_data) # evt principal courant
        self.return_created_data = return_created_data
        
        self.not_main_event = {'TextInsert', 'ShellInput', 'DebuggerResponse'}

    # L'event passé en param est une donnée sélectionnée/nettoyée à partir
    # d'un event Thonny, dc data dans la terminologie du mainApp
    def read_event(self, data : dict) -> None :
        """
        Read an event to get it's data and formats them in an intermediate format. 
        If it a new event flush the data of the last one.

        Args:
            data (obj:'def(dict)'): The initial data of event from Thonny.
        """
        # not not = id :(
        if data['sequence'] not in self.not_main_event :
            # evt principal : devient self.currentEvent
            self.flush()
            self.currentEvent = self._create_event(data)
        # c'est tjs l'evt principal qui exécute le read_event    
        self.currentEvent.read_event(data)

    def _create_event(self, data : dict) -> Event :
        """
        Create à Event class corresponding to the receveid data from the event.

        Args:
            data (obj:'def(dict)'): The initial data of event from Thonny.

        Return:
            (obj:'Event'): The corresponding Event class.
        """

        if(data['sequence'] != 'ShellCommand') :
            return self.factory.create_event(data['sequence'], self.return_created_data)
        
        # ce code concerne dc uniquement les ShellCommand
        command : str = data['command_text']

        # commande équivalente à 'Python3 file.py'
        if(command.startswith('%Run')) :
            return self.factory.create_event('Run_program', self.return_created_data)

        if(command.startswith('%L1test')) :
            return self.factory.create_event(None, self.return_created_data)

        if(command.startswith('%Debug')) :
            return self.factory.create_event('Run_debugger', self.return_created_data)

        return self.factory.create_event('Run_command', self.return_created_data)

    def flush(self) :
        """
        Send the data of the current event and reset the class.
        """

        self.currentEvent.flush()

    def parse_to_xAPI(self, formated_data: dict) -> dict :
        """
        Parse the formated data (obtened by flush after using read_event) to receive them in the xApi format.

        Args:
            formated_data (obj:'dict'): The data in the intermediate format.

        Return:
            (obj:'dict'): The parsed data in xApi format.
        """

        event = self.factory.create_event(formated_data['eventType'], self.return_created_data)
        return event.parse_to_xAPI(formated_data)
