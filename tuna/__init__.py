# some constants
LOG_TIMESTAMP = "%Y-%m-%d %H:%M:%S"
GLOBAL_NAME = "TUNA"
SECTION = "TUNA"
MODULES_SECTION = 'MODULES'
VERSION = "2014.06.12"
FILE_TIMESTAMP = "%Y_%m_%d_%I:%M:%S_%p"
BLUE = "\033[34m"
RED  = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0;0m"
NEWLINE = '\n'
BLUE_BOLD_RESET = BLUE + BOLD + "{0}" + RESET
BOLD_RESET = BOLD + "{0}" + RESET

RED_THING =  "{red}{{{{thing}}}}{reset} {{verb}}".format(red=RED, reset=RESET)
BOLD_THING = "{bold}{{thing}}{reset} {{{{value}}}}".format(bold=BOLD, reset=RESET)
ARGS = BOLD_THING.format(thing='Args:')
KWARGS = BOLD_THING.format(thing='Kwargs:')
CREATION = RED_THING.format(verb='Created')
CALLED_ON = "'{blue}{{attribute}}{reset}' attribute called on {red}{{thing}}{reset}".format(blue=BLUE,
                                                                                             red=RED,
                                                                                             reset=RESET)
CALLED = RED_THING.format(verb='Called')
NOT_IMPLEMENTED = RED_THING.format(verb='Not Implemented')

# common imports
class TunaError(Exception):
    """
    An exception for the top-level code (catch all predictable errors)
    """

class ConfigurationError(TunaError):
    """
    An Error for configuration problems
    """

class DontCatchError(Exception):
    """
    A sibling to the configuration error that should crash the program if raised
    """

from tuna.infrastructure.baseclass import BaseClass
from tuna.infrastructure.baseconfiguration import BaseConfiguration
from tuna.plugins.base_plugin import BasePlugin
from tuna.components.component import BaseComponent
from tuna.parts.dummy.dummy import DummyClass    
