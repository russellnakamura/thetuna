
# python standard library
from collections import OrderedDict

# this package
from tuna.infrastructure import singletons
from tuna import GLOBAL_NAME
from base_plugin import BasePlugin
from tuna.parts.storage.storageadapter import StorageAdapter
from tuna.hosts.host import TheHost, HostConfiguration

from tuna.commands.watcher import TheWatcher, WatcherConstants
from tuna.components.composite import SimpleComposite



SECTION = 'CommandWatcher'
CONFIGURATION = '''[{section}]
# the section-name has to match an option in the TUNA section
# the plugin has to be the actual class name
plugin = CommandWatcher

# the connection should be the name of a section in the config
# that has information to setup a connection to the device
connection = DUT

# the mode should be either 'a' (append to one file)
# or 'w' (write to separate files)
# mode = w

# the commands to dump should take the form
<identifier 1> = <command 1>
<identifer 2> = <command 2>
'''.format(section=SECTION)


class CommandWatcher(BasePlugin):
    """
    A composite to watch command output
    """
    def __init__(self, *args, **kwargs):
        """
        CommandWatcher plugin Constructor

        """
        super(CommandWatcher, self).__init__(*args, **kwargs)
        self._storage = None
        return

    @property
    def storage(self):
        """
        A storage for command output
        """
        if self._storage is None:
            storage = singletons.get_filestorage(name=GLOBAL_NAME)
            self._storage = storage
        return self._storage                

    @property
    def sections(self):
        """
        An ordered dictionary for the HelpPage
        """
        if self._sections is None:
            bold = '{bold}'
            reset = '{reset}'
            name = 'CommandWatcher'
            bold_name = bold + name + reset

            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- a command watcher'
            self._sections['Description'] = bold_name + ' stores the output of a command in the background.'
            self._sections["Configuration"] = CONFIGURATION
            self._sections['Files'] = __file__
        return self._sections
    
    def host_builder(self, section):
        configuration = HostConfiguration(configuration=self.configuration,
                                                     section=section)
        client = TheHost(hostname=configuration.control_ip,
                         test_interface=configuration.test_ip,
                        username=configuration.username,
                        timeout=configuration.timeout,
                        prefix=configuration.prefix,
                        operating_system=configuration.operating_system,
                        connection_type=configuration.connection_type,
                        **configuration.kwargs)
        return client

    @property
    def product(self):
        """
        This is the CommandWatcher product

        To allow repeated running the CommandWatcher is created anew every time

        :precondition: self.configuration is a configuration map
        """
        kwargs = dict(self.configuration.items(section=self.section_header,
                                                   optional=False))
        self.logger.debug("Building the CommandWatcher with: {0}".format(kwargs))

        connection_section = self.configuration.get(section=self.section_header,
                                                    option='connection')
        client = self.host_builder(connection_section)
        mode = self.configuration.get(section=self.section_header,
                                        option='mode',
                                            optional=True,
                                            default=WatcherConstants.default_mode)
        options = 'connection mode plugin component'.split() + self.configuration.defaults.keys()
        identifiers = [identifier for identifier in self.configuration.options(self.section_header)
                       if identifier not in options]
        self._product = SimpleComposite()
        for identifier in identifiers:
            self._product.add(TheWatcher(command=self.configuration.get(section=self.section_header,
                                                                        option=identifier),
                                                                        storage=self.storage,
                                                                        connection=client,
                                                                        identifier=identifier,
                                                                        mode=mode))
        return self._product
        
    def fetch_config(self):
        """
        Prints example configuration to stdout
        """
        print CONFIGURATION
# end class CommandWatcher
