from .event import Event
from thonnycontrib.thonny_LoggingPlugin.configuration.configXApi import EVENTTYPE_TO_VERB_ID, OBJECTS_URI, MAXIMUM_BUFFER_SIZE, OVERFLOX_BUFFER_TEXT

class EventShellDebugger(Event) :
    """
    The event class who represents debugger action
    """

    def _init_data(self) -> dict:
        """
        Initialize the data with its key, using their values if there was static or else using None.

        Return:
            (obj:'dict'): The initialized data for this event.
        """

        return {
            'timestamp_begin' : None,
            'timestamp_end' : None,
            'timestamp_actions' : [],
            'eventID' : None,
            'sessionID' : None,
            'actors' : None,
            'research_usage' : None,
            'command' : None,
            'codestate' : None,
            'eventType' : 'Run_debugger',
            'status' : True,
            'stdin' : '', 
            'stdout' : '', 
            'stderr' : '',
            'filename' : None,
            'lineno' : None,
            'codestate' : None
        }

    # Modifié par Mirabelle pour capter le filename, le codestate
    # et le lineno du pt d'arrêt du débugger.
    def read_event(self, event : dict) -> None :
        """
        Read a event to get it's data and formats them in an intermediate format.

        Args:
            event (obj:'def(dict)'): The initial data of event from Thonny.
        """

        # new event
        if self.state == 'on progress' :
            # le 1er evt qui suit le clic sur le cafard est un ShellCommand
            # on récupère le codestate
            if event['sequence'] == 'ShellCommand' :
                self.data['timestamp_begin'] = event['time']
                self.data['timestamp_actions'] = []
                self.data['eventID'] = event['eventID']
                self.data['actors'] = event['actors']
                self.data['sessionID'] = event['sessionID']
                self.data['research_usage'] = event['research_usage']
                self.data['codestate'] = event['editorContent']
                # le nom du fichier apparaît ds la commande
                self.data['command'] = event['command_text']

            # ensuite ds le cas nominal il arrive des DebuggerResponse
            # ds le 1er on récupère le lineno qui est celui du pt d'arrêt
            # et le filename
            # ds les suivants on ne récupère pas le lineno qui évolue au fil du debug,
            # ni le filename qui reste inchangé
            # Ds tous les cas on récupère le time_stamp
            elif event['sequence'] == 'DebuggerResponse' :
                self.data['timestamp_actions'].append(event['time'])              
                # 1er evt : récup info point d'arrêt
                # peut-être toujours présence de stack non vide, je ne sais pas
                if len(self.data['timestamp_actions'])== 1  \
                   and 'stack' in event \
                   and len(event['stack']) > 0:
                    frame_info = event['stack'][0]
                    self.data['filename'] = frame_info.filename
                    self.data['codestate'] = frame_info.source
                    self.data['lineno'] = frame_info.lineno
                # Pour tous les evts :
                # Supprimer l'objet stack qui n'est pas sérialisable
                # et ne sert qu'à récupérer les infos utiles
                # -> ne pas le mettre dans le json
                # -> deepcopy dans les tests
                del event['stack'] 

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
                    self.data['timestamp_end'] = event['time']
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
            'timestamp' : formated_data['timestamp_begin'],
            'research_usage' : formated_data['research_usage'],
            'verb' : {
                'id' : EVENTTYPE_TO_VERB_ID[formated_data['eventType']]
            },
            'actor' : {
                "openid" :'https://www.cristal.univ-lille.fr/users/' + binome1 + '/' + binome2
            },
            'object' : {
                'id' : OBJECTS_URI['debugger'],
                'extension' : {
                    OBJECTS_URI['command'] + '/CommandRan' : formated_data['command'],
                    OBJECTS_URI['debugger'] + '/TimeStampEnd' : formated_data['timestamp_end'],
                    OBJECTS_URI['debugger'] + '/TimeStampActions' : formated_data['timestamp_actions'],
                    OBJECTS_URI['program'] + '/CodeState' : formated_data['codestate'],
                    OBJECTS_URI['debugger'] + '/Lineno' : formated_data['lineno'],
                    OBJECTS_URI['file'] + '/Filename' : formated_data['filename']
                }
            },
            'context' : {
                'extension' : { 
                    OBJECTS_URI['session'] +'/ID' : str(formated_data['sessionID']) 
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
