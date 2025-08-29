from .event import Event
from .event_open import EventOpen
from .event_save import EventSave
from .event_startSession import EventStartSession
from .event_endSession import EventEndSession
from .event_shellCommand import EventShellCommand
from .event_shellProgram import EventShellProgram
from .event_shellDebugger import EventShellDebugger
from .event_l1Tests import EventL1Tests
from .event_notReferenced import EventNotReferenced
from .event_l1TestsDocGenerator import EventL1TestsDocGenerator

class EventFactory() :
    """
    A factory to create each type of Event.
    """

    def create_event(self, name : str, return_created_data) -> Event :
        """
        Create à Event class corresponding to the receveid name or a event_notReferenced if the name is unknow.

        Args:
            name (obj:'str'): The name of the event.
            return_created_data (obj:'def(dict)'): The function to call back to return the data of event when this one is flush.

        Return:
            (obj:'Event'): The corresponding Event class.
        """

        match name :
            case 'Open' :
                return EventOpen(return_created_data)

            case 'Save' :
                return EventSave(return_created_data)

            case 'SaveAs' :
                return EventSave(return_created_data)

            case 'Run_command' :
                return EventShellCommand(return_created_data)

            case 'Run_program' :
                return EventShellProgram(return_created_data)

            case 'Run_debugger' :
                return EventShellDebugger(return_created_data)

            case 'l1Tests' :
                return EventL1Tests(return_created_data)

            case 'Session_start' :
                return EventStartSession(return_created_data)

            case 'Session_end' :
                return EventEndSession(return_created_data)

            case 'l1Tests.DocGenerator' :
                return EventL1TestsDocGenerator(return_created_data)

            case _ :
                return EventNotReferenced(return_created_data)