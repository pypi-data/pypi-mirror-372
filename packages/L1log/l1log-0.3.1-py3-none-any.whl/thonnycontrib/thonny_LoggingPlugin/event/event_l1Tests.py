from .event import Event
from thonnycontrib.thonny_LoggingPlugin.configuration.configXApi import EVENTTYPE_TO_VERB_ID, OBJECTS_URI

class EventL1Tests(Event) :
    """
    The event class who represents l1Test event after the shell command for him is run.
    """


    def _init_data(self) -> dict:
        """
        Initialize the data with its key, using their values if there was static or else using None.

        Return:
            (obj:'dict'): The initialized data for this event.
        """

        return {
                'timestamp' : None,
                'eventID' : None,
                'sessionID' : None,
                'actors' : None,
                'research_usage' : None,
                'filename' : None,
                'codestate' : None,
                'tests' : None,
                'eventType' : 'l1Tests'
            }

    def read_event(self, event : dict) -> None :
        """
        Read a event to get it's data and formats them in an intermediate format.

        Args:
            event (obj:'def(dict)'): The initial data of event from Thonny.
        """

        # new event
        if self.state == 'on progress' :
            if event['sequence'] == 'l1Tests' :
                self.data['timestamp'] = event['time']
                self.data['eventID'] = event['eventID']
                self.data['actors'] = event['actors']
                self.data['sessionID'] = event['sessionID']
                self.data['research_usage'] = event['research_usage']
                self.data['filename'] = event['filename']
                self.data['codestate'] = event['editorContent']
                self.data['tests'] = event['tests']

                self.state =  'completed'
                
        # event already completed
        elif self.state == 'completed' :
            pass

    def parse_to_xAPI(self, formated_data: dict) -> dict:
        """
        Parse the formated data (obtened by flush after using read_event) to receive them in the xApi format.

        Args:
            formated_data (obj:'dict'): The data in the intermediate format.

        Return:
            (obj:'dict'): The parsed data in xApi format.
        """
        
        (binome1, binome2) = formated_data['actors']
        if not binome2:
            binome2 = ""

        return {
            'timestamp' : formated_data['timestamp'],
            'research_usage' : formated_data['research_usage'],
            'verb' : {
                'id' : EVENTTYPE_TO_VERB_ID[formated_data['eventType']]
            },
            'actor' : {
                "openid" :'https://www.cristal.univ-lille.fr/users/' + binome1 + '/' + binome2
            },
            'object' : {
                'id' : OBJECTS_URI['test'],
                'extension' : {
                    OBJECTS_URI['file'] + '/Filename' : formated_data['filename'],
                    OBJECTS_URI['test'] + '/Tests'  : formated_data['tests'],
                    OBJECTS_URI['program'] + '/CodeState' : formated_data['codestate']
                }
            },
            'context' : {
                'extension' : { 
                    OBJECTS_URI['session'] +'/ID' : str(formated_data['sessionID']) 
                }
            }
        }
