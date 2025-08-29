from abc import ABC, abstractmethod
from thonnycontrib.thonny_LoggingPlugin.configuration.configXApi import EVENTTYPE_TO_VERB_ID, OBJECTS_URI 

class Event(ABC) :
    """
    The abstract class who represents any event.
    """

    def __init__(self, return_created_data) :
        """
        Initialize the class Event.

        Args:
            return_created_data (obj:'def(dict)'): The function to call back to return the data of event when flush.
        """

        self.return_created_data = return_created_data
        self.data = self._init_data()
        self.state = 'on progress'

    def flush(self) -> None: 
        """
        Send the data of event and reset the class.
        """

        self.return_created_data(self.data)
        self.data = self._init_data()
        self.state = 'on progress'

    @abstractmethod
    def _init_data(self) -> dict:
        """
        Initialize the data with its key, using their values if there was static or else using None.

        Return:
            (obj:'dict'): The initialized data for this event.
        """
        pass

    @abstractmethod
    def read_event(self, event : dict) -> None :
        """
        Read a event to get it's data and formats them in an intermediate format.

        Args:
            event (obj:'def(dict)'): The initial data of event from Thonny.
        """
        pass

    @abstractmethod
    def parse_to_xAPI(self, formated_data: dict) -> dict :
        """
        Parse the formated data (obtened by flush after using read_event) to receive them in the xApi format.

        Args:
            formated_data (obj:'dict'): The data in the intermediate format.

        Return:
            (obj:'dict'): The parsed data in xApi format.
        """
        pass