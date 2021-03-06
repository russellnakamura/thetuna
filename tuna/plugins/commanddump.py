
# python standard library
from collections import OrderedDict

# this package
from tuna.infrastructure import singletons
from tuna import GLOBAL_NAME
from base_plugin import BasePlugin
from tuna.parts.storage.storageadapter import StorageAdapter
from tuna.hosts.host import TheHost, HostConfiguration

from tuna.commands.dump import TheDump, DumpConstants
from tuna.components.composite import SimpleComposite



in_pweave = __name__ == '__builtin__'


SECTION = 'CommandDump'
CONFIGURATION = '''[{section}]
# the section-name has to match an option in the TUNA section
# the plugin has to be the actual class name
plugin = CommandDump

# the connection should be the name of a section in the config
# that has information to setup a connection to the device
connection = DUT

# the timeout is a readline timeout for the
#  connection to the device
# timeout = 5

# the mode should be either 'a' (append to one file)
# or 'w' (write to separate files)
# mode = w

# the commands to dump should take the form
<identifier 1> = <command 1>
<identifer 2> = <command 2>
'''.format(section=SECTION)


output_documentation = __name__ == '__builtin__'


class CommandDump(BasePlugin):
    """
    A composite to dump command output
    """
    def __init__(self, *args, **kwargs):
        """
        CommandDump plugin Constructor

        """
        super(CommandDump, self).__init__(*args, **kwargs)
        self._storage = None
        return

    @property
    def storage(self):
        """
        A storage for command output
        """
        if self._storage is None:
            #filename =  self.configuration.get(section=self.section_header,
            #                                  option='store_output',
            #                                  optional=True)
            storage = singletons.get_filestorage(name=GLOBAL_NAME)

            self._storage = storage
            #else:
            #    self._storage = NullStorage()
        return self._storage                

    @property
    def sections(self):
        """
        An ordered dictionary for the HelpPage
        """
        if self._sections is None:
            bold = '{bold}'
            reset = '{reset}'
            name = 'CommandDump'
            bold_name = bold + name + reset

            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- a command dump'
            self._sections['Description'] = bold_name + ' stores the output of a command.'
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
        This is the CommandDump product

        To allow repeated running the CommandDump is created anew every time

        :precondition: self.configuration is a configuration map
        """
        kwargs = dict(self.configuration.items(section=self.section_header,
                                                   optional=False))
        self.logger.debug("Building the CommandDump with: {0}".format(kwargs))

        connection_section = self.configuration.get(section=self.section_header,
                                                    option='connection')
        client = self.host_builder(connection_section)
        timeout = self.configuration.get_float(section=self.section_header,
                                               option='timeout',
                                               optional=True,
                                               default=DumpConstants.default_timeout)
        mode = self.configuration.get(section=self.section_header,
                                        option='mode',
                                            optional=True,
                                            default=DumpConstants.default_mode)
        options = 'connection timeout mode plugin component'.split() + self.configuration.defaults.keys()
        identifiers = [identifier for identifier in self.configuration.options(self.section_header)
                       if identifier not in options]
        self._product = SimpleComposite()
        for identifier in identifiers:
            self._product.add(TheDump(command=self.configuration.get(section=self.section_header,
                                                                     option=identifier),
                                                                     storage=self.storage,
                                                                     connection=client,
                                                                     identifier=identifier,
                                                                     timeout=timeout,
                                                                     mode=mode))
        return self._product
        
    def fetch_config(self):
        """
        Prints example configuration to stdout
        """
        print CONFIGURATION
# end class CommandDump
