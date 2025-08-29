from .event import Event

# unwanted event
class EventNotReferenced(Event) :
    """
    The event class who represents a event who is not referenced (or unwanted);
    """

    # return empty data
    def _init_data(self) -> dict:
        """
        Initialize the data with its key, using their values if there was static or else using None. (return empty dict)

        Return:
            (obj:'dict'): The initialized data for this event.
        """
        return {}

    # do nothing
    def flush(self) -> None: 
        """
        Send the data of event and reset the class. (do nothing)
        """
        pass

    # do nothing
    def read_event(self, event : dict) -> None :
        """
        Read a event to get it's data and formats them in an intermediate format. (do nothing)

        Args:
            event (obj:'def(dict)'): The initial data of event from Thonny.
        """
        pass

    # return empty data
    def parse_to_xAPI(self, formated_data: dict) -> dict:
        """
        Parse the formated data (obtened by flush after using read_event) to receive them in the xApi format. (return empty dict)

        Args:
            formated_data (obj:'dict'): The data in the intermediate format.

        Return:
            (obj:'dict'): The parsed data in xApi format.
        """
        return {}
