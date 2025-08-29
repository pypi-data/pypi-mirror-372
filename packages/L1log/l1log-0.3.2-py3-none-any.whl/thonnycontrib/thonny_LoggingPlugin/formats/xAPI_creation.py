# This script has as goal to convert data to the format xAPI 

EVENTTYPE_TO_VERB_ID = {
    'Run_program'   : 'https://www.cristal.univ-lille.fr/verbs/Run.Program',
    'Run_command'   : 'https://www.cristal.univ-lille.fr/verbs/Run.Command',
    'Open'          : 'https://www.cristal.univ-lille.fr/verbs/File.Open',
    'Save'          : 'https://www.cristal.univ-lille.fr/verbs/File.Save',
    'Session_start' : 'https://www.cristal.univ-lille.fr/verbs/Session.Start',
    'Session_end'   : 'https://www.cristal.univ-lille.fr/verbs/Session.End',
    'l1Tests'       : 'https://www.cristal.univ-lille.fr/verbs/Run.test',
    'l1Tests.DocGenerator' : 'https://www.cristal.univ-lille.fr/verbs/Docstring.Generate',
}

OBJECTS_URI = {
    'file'    : 'https://www.cristal.univ-lille.fr/objects/File',
    'command' : 'https://www.cristal.univ-lille.fr/objects/Command',
    'session' : 'https://www.cristal.univ-lille.fr/objects/Session',
    'test'    : 'https://www.cristal.univ-lille.fr/objects/Tests',
    'program' : 'https://www.cristal.univ-lille.fr/objects/Program',
    'plugin'  : 'https://www.cristal.univ-lille.fr/objects/Plugin',
    'docstring' : 'https://www.cristal.univ-lille.fr/objects/DocString',
}

def convert_to_xAPI(data):
    """
    Convert the data to xAPI format
    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): the data to xAPI format

    """
    statement = {
        'timestamp' : data['timestamp'],
        'research_usage' : data['research_usage'],
        'verb' : create_verb(data),
        'actor' : create_actor(data),
        'object' : create_object(data),
        'context' : create_context(data)
    }
    # Une suite de tests n'a pas de résultat, un test en a un
    if data['eventType'] in {'Run_program','Run_command'}:
        statement['result'] = create_result(data)

    return statement

def create_actor(data):
    """
    Create an xAPI actor from the data

    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): an actor from the xAPI format
    """
    # modifié car ce n'est pas une URL
    (binome1, binome2) = data['actors']
    if not binome2:
        binome2 = ""
    return {"openid" :'https://www.cristal.univ-lille.fr/users/' + binome1 + '/' + binome2}

def create_verb(data):
    """
    Create an xAPI verb from the data

    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): an verb from the xAPI format
    """
    return {'id' : EVENTTYPE_TO_VERB_ID[data['eventType']]}

def create_object(data):
    """
    Create an xAPI object from the data

    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): an object from the xAPI format
    """
    object = dict()
    type = data['eventType']
    if type in ('Open','Save'):
        object['id'] = OBJECTS_URI['file']

        object['extension'] = {
            OBJECTS_URI['file']+'/Filename' : data['filename'],
            OBJECTS_URI['file']+'/CodeState' : data['codestate']
        }

    elif type == 'Run_program':
        object['id'] = OBJECTS_URI['program']
        object['extension'] = {
            OBJECTS_URI['command'] + '/CommandRan' : data['command'],
            OBJECTS_URI['program'] + '/CodeState' : data['codestate']
            }

    elif type == 'Run_command' :
        object['id'] = OBJECTS_URI['command']
        object['extension'] = {OBJECTS_URI['command'] + '/CommandRan' : data['command']}
    
    elif type in {'Session_start','Session_end'} :
        object['id'] = OBJECTS_URI['session']

    # Modif pour L1test V3
    elif type == 'l1Tests':
        object['id'] = OBJECTS_URI['test']
        object['extension'] = {
            OBJECTS_URI['file'] + '/Filename' : data['filename'],
            OBJECTS_URI['test'] + '/Tests'  : data['tests'],
            OBJECTS_URI['program'] + '/CodeState' : data['codestate']
        }
    elif type == 'l1Tests.DocGenerator':
        object['id'] = OBJECTS_URI['docstring']
        object['extension'] = {
            OBJECTS_URI['docstring'] + '/Function': data['name']
        }
    
    else :
        raise Exception("Error : eventType not accepted")
    
    return object

def create_result(data):
    """
    Create an xAPI result from the data

    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): an result from the xAPI format
    """
    result = {
        "success" : data['status']
    }

    if data['eventType'] in {'Run_program','Run_command'}:

        result['extension'] = {
                OBJECTS_URI['command'] +'/stdin'     : data['stdin'],
                OBJECTS_URI['command'] +'/stdout'    : data['stdout'],
                OBJECTS_URI['command'] +'/stderr'    : data['stderr'],
                }

    return result

def create_context(data):
    """
    Create an xAPI context from the data

    Args :
        data (object: dict()): the data to convert
    Return :
        (object: dict()): an context from the xAPI format
    """
    context = {'extension' : { OBJECTS_URI['session'] +'/ID' : str(data['sessionID']) }}

    return context

