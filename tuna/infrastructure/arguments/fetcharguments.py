
"""fetch subcommand
    
usage: tuna fetch -h
       tuna fetch [<name>...]  [--module <module> ...] [-c]

positional arguments:
    <name>                         List of plugin-names (default=['Optimizer'])

optional arguments:
    -h, --help                     Show this help message and exit
    -c, --components               If set, looks for `components` instead of `plugins`
    -m, --module <module> ...      Non-optimizer modules
"""


# the Tuna
from tuna.infrastructure.arguments.arguments import BaseArguments
from tuna.infrastructure.arguments.basestrategy import BaseStrategy
from tuna.infrastructure.crash_handler import try_except


class FetchArgumentsConstants(object):
    """
    Constants for the `fetch` sub-command arguments
    """    
    __slots__ = ()
    # arguments and options
    names = "<name>"
    modules = '--module'
    components = '--components'
    
    # defaults
    default_names = ['Tuna']


class Fetch(BaseArguments):
    """
    fetch a sample configuration
    """
    def __init__(self, *args, **kwargs):
        super(Fetch, self).__init__(*args, **kwargs)
        self.sub_usage = __doc__
        self._names = None
        self._modules = None
        self._function = None
        self._components = None
        return

    @property
    def function(self):
        """
        fetch sub-command
        """
        if self._function is None:
            self._function = FetchStrategy().function
        return self._function

    @property
    def names(self):
        """
        List of plugin names to use
        """
        if self._names is None:
            self._names = self.sub_arguments[FetchArgumentsConstants.names]
            if not self._names:
                self._names = FetchArgumentsConstants.default_names
        return self._names

    @property
    def components(self):
        """
        Flag to use components instead of plugins
        """
        if self._components is None:
            self._components = self.sub_arguments[FetchArgumentsConstants.components]
        return self._components

    @property
    def modules(self):
        """
        List of modules holding plugins
        """
        if self._modules is None:
            self._modules = self.sub_arguments[FetchArgumentsConstants.modules]
        return self._modules
    
    def reset(self):
        """
        Resets the attributes to None
        """
        super(Fetch, self).reset()
        self._modules = None
        self._names = None
        return
# end FetchArguments    


class FetchStrategy(BaseStrategy):
    """
    A strategy for the `fetch` sub-command
    """
    @try_except
    def function(self, args):
        """
        'fetch' a sample plugin config-file

        :param:

         - `args`: namespace with 'names' and 'modules' list attributes
        """
        if args.components:
            self.quartermaster.name = 'components'
            self.quartermaster.exclusions.append('tuna.components.composite')

        for name in args.names:
            self.logger.debug("Getting Plugin: {0}".format(name))
            self.quartermaster.external_modules = args.modules

            # the quartermaster returns definitions, not instances
            try:
                plugin = self.quartermaster.get_plugin(name)
                config = plugin().fetch_config()
            except TypeError as error:
                self.logger.debug(error)
                if "Can't instantiate" in error[0]:
                    self.log_error(error="Plugin Implementation Error: ",
                                   message="{0}".format(error))
                else:
                    self.log_error(error="Unknown Plugin: ",
                                   message='{0}'.format(name))
        return
