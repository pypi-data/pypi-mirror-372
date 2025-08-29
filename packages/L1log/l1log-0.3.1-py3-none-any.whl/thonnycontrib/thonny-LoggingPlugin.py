from thonnycontrib.thonny_LoggingPlugin.configuration.configBinome import set_binome
from thonnycontrib.thonny_LoggingPlugin.configuration.globals import URL_TERMS_OF_USE, WB
from thonnycontrib.thonny_LoggingPlugin import mainApp

from thonnycontrib.thonny_LoggingPlugin.configuration import configuration
from thonnycontrib.thonny_LoggingPlugin.popups.l1log_popups import display_about_plugin, display_terms_of_use, display_binome_request, LDAP_OK, LDAP_KO
from thonnycontrib.thonny_LoggingPlugin.popups.ldap_connection import get_identifiers

import os
import getpass

import ldap

def load_plugin():
    """
    Load the plugin and and a command to configure it in thonny
    """
    configuration.init_options()

    current_groups = os.getgroups()
    current_groups.append(os.getuid())
    # Vérifie la présence de l'élève dans le groupe d'élèves compris dans la recherche
    if any(usergroup in configuration.get_option("authorized_groups") for usergroup in current_groups):
        if configuration.get_option("first_run"):
            reponse = display_terms_of_use()
            configuration.accept_terms_of_uses(reponse)
            WB.set_option("loggingPlugin.first_run", False)
        user1 = getpass.getuser()

        try:
            ldap_conn = ldap.initialize('ldap://ldaphost.fil.univ-lille.fr')
            identifiers = get_identifiers(ldap_conn)
            actors = display_binome_request(user1, identifiers, mode=LDAP_OK)
        except ldap.SERVER_DOWN as e:
            actors = display_binome_request(user1, identifiers=None, mode=LDAP_KO)
        except BaseException as e:
            actors = display_binome_request(user1, identifiers=None, mode=LDAP_KO)

        logger = mainApp.EventLogger(actors)
        WB.add_configuration_page("LoggingPlugin", "LoggingPlugin", configuration.plugin_configuration_page, 30)

        WB.add_command(command_id="about_logger",
                       menu_name="tools",
                       command_label="Logging Plugin",
                       handler=display_about_plugin)

# eof


