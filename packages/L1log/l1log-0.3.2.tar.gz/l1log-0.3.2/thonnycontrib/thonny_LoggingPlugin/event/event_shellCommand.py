from .event import Event
from thonnycontrib.thonny_LoggingPlugin.configuration.configXApi import EVENTTYPE_TO_VERB_ID, OBJECTS_URI, MAXIMUM_BUFFER_SIZE, OVERFLOX_BUFFER_TEXT

class EventShellCommand(Event) :
    """
    The event class who represents a shell command other than one who run a program.
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
            'command' : None,
            'eventType' : 'Run_command',
            'status' : True,
            'stdin' : '', 
            'stdout' : '', 
            'stderr' : '',
            }

    def read_event(self, event : dict) -> None :
        """
        Read a event to get it's data and formats them in an intermediate format.

        Args:
            event (obj:'def(dict)'): The initial data of event from Thonny.
        """

        # new event
        if self.state == 'on progress' :
            if event['sequence'] == 'ShellCommand' :
                self.data['timestamp'] = event['time']
                self.data['eventID'] = event['eventID']
                self.data['actors'] = event['actors']
                self.data['sessionID'] = event['sessionID']
                self.data['research_usage'] = event['research_usage']
                self.data['command'] = event['command_text']
                # le nom du fichier apparaît ds la commande --> ??? pas pour une commande dans l'interpréteur de Thonny


            elif event['sequence'] == 'ShellInput':
                self.data['stdin'] += event['input_text']
                
            elif event['sequence'] == 'TextInsert' :
                if event['tags'] == None:
                    return

                if 'stdout' in event['tags'] or 'value' in event['tags']:
                    self.data['stdout'] += event['text']
                
                if 'stderr' in event['tags']:
                    self.data['stderr'] += event['text']
                    self.data['status'] = False

                if 'prompt' in event['tags'] :
                    self.state = 'completed'

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
                'id' : OBJECTS_URI['command'],
                'extension' : {
                    OBJECTS_URI['command'] + '/CommandRan' : formated_data['command']
                }
            },
            'context' : {
                'extension' : { 
                    OBJECTS_URI['session'] +'/ID' : str(formated_data['sessionID']),
                    #OBJECTS_URI['file']+'/Filename' : formated_data['filename'],
                }
            },
            'result' : {
                'success' : formated_data['status'],
                'extension' : {
                    OBJECTS_URI['command'] +'/stdin' : formated_data['stdin'] if len(formated_data['stdin']) <= MAXIMUM_BUFFER_SIZE else OVERFLOX_BUFFER_TEXT,
                    OBJECTS_URI['command'] +'/stdout' : formated_data['stdout'] if len(formated_data['stdout']) <= MAXIMUM_BUFFER_SIZE else OVERFLOX_BUFFER_TEXT,
                    OBJECTS_URI['command'] +'/stderr' : formated_data['stderr'] if len(formated_data['stderr']) <= MAXIMUM_BUFFER_SIZE else OVERFLOX_BUFFER_TEXT,
                }
            }
        }
