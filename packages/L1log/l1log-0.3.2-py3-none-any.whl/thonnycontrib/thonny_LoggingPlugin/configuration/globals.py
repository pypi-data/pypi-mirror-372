from thonny import THONNY_USER_DIR, get_workbench

# Groupes pour lesquels on lance le plugin de log
# Groupe unix ou UID utilisateur
# ex : MI = 1100
AUTHORIZED_GROUPS = [1100]

# Default config
DEFAULT_PATH = THONNY_USER_DIR + "/LoggingPlugin/"
DEFAULT_SERVER = 'http://127.0.0.1:8081'  # 'http://localhost:8081'
DEFAULT_STORE = True
DEFAULT_RESEARCH_USAGE = False
DEFAULT_LOG_IN_CONSOLE = False

URL_TERMS_OF_USE = "https://www.fil.univ-lille.fr/~L1S1Info/MI/collecte_donnees_thonny.pdf"

# Dict of options name and default value
OPTIONS = {
    "local_path": DEFAULT_PATH,
    "server_address": DEFAULT_SERVER,
    "store_logs": DEFAULT_STORE,
    "log_in_console": DEFAULT_LOG_IN_CONSOLE,
    "research_usage_logs": DEFAULT_RESEARCH_USAGE,
    "first_run": True,
    "authorized_groups": AUTHORIZED_GROUPS
}

# Get the thonny workbench object
WB = get_workbench()
