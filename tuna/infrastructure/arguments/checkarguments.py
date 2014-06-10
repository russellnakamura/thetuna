
"""`check` sub-command

usage: tuna check -h
       tuna check  [<config-file-name> ...] [--module <module> ...]

Positional Arguments:

    <config-file-name> ...    List of config files (e.g. *.ini - default='['tuna.ini']')

optional arguments:

    -h, --help                  Show this help message and exit
    -m, --module <module>       Non-tuna module with plugins

"""


# third-party
import docopt

# this package
from tuna.infrastructure.arguments.arguments import BaseArguments, ArgumentsConstants
from tuna.infrastructure.arguments.basestrategy import BaseStrategy
from tuna.infrastructure.crash_handler import try_except


class CheckArgumentsConstants(object):
    """
    A holder of constants for the Check Sub-Command Arguments
    """
    __slots__ = ()
    # options and arguments
    configfilenames = "<config-file-name>"
    modules = "--module"

    #defaults
    default_configfilenames = ['tuna.ini']


class Check(BaseArguments):
    """
    Check a configuration
    """
    def __init__(self, *args, **kwargs):
        super(Check, self).__init__(*args, **kwargs)
        self._configfiles = None
        self._modules = None
        self.sub_usage = __doc__
        self._function = None
        return

    @property
    def function(self):
        """
        The `check` sub-command 
        """
        if self._function is None:
            self._function = CheckStrategy().function
        return self._function

    @property
    def configfiles(self):
        """
        List of configuration file names.
        """
        if self._configfiles is None:
            self._configfiles = self.sub_arguments[CheckArgumentsConstants.configfilenames]
            if not self._configfiles:
                self._configfiles = CheckArgumentsConstants.default_configfilenames
        return self._configfiles

    @property
    def modules(self):
        """
        List of optional modules
        """
        if self._modules is None:
            self._modules = self.sub_arguments[CheckArgumentsConstants.modules]
        return self._modules
    
    def reset(self):
        """
        Resets the properties to None
        """
        super(Check, self).reset()
        self._sub_arguments = None
        self._configfiles = None
        self._modules = None
        return
#end Check    


class CheckStrategy(BaseStrategy):
    """
    The `check` sub-command strategy
    """
    @try_except
    def function(self, args):
        """
        Builds the tuna and checks the configuration(s)

        :param:

         - `args`: object with configfiles for to build the tuna
        """
        tuna = self.build_tuna(args.configfiles)
        if tuna is None:
            return
        tuna.check_rep()
        return
# end CheckStrategy    
