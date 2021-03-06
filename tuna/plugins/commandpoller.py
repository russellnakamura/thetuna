
# python standard library
from collections import OrderedDict

# this package
from tuna.infrastructure import singletons
from tuna import GLOBAL_NAME
from base_plugin import BasePlugin
from tuna.parts.storage.storageadapter import StorageAdapter
from tuna.hosts.host import TheHost, HostConfiguration

from tuna.commands.poller import PollerBuilder, PollerConfiguration
from tuna.commands.poller import EXAMPLE_CONFIGURATION as POLLER_EXAMPLE


in_pweave = __name__ == '__builtin__'


SECTION = 'CommandPoller'
CONFIGURATION = """
[{section}]
# the section-name has to match an option in the TUNA section
# the plugin has to be the actual class name
plugin = CommandPoller

# the connection should be the name of a section in the config
# that has information to setup a connection to the device
connection = DUT

{poller_example}
""".format(section=SECTION,
           poller_example=POLLER_EXAMPLE)


output_documentation = __name__ == '__builtin__'


class CommandPoller(BasePlugin):
    """
    A threaded command to csv-file plugin
    """
    def __init__(self, *args, **kwargs):
        """
        CommandPoller plugin Constructor

        """
        super(CommandPoller, self).__init__(*args, **kwargs)
        self._storage = None
        self._poller_configuration = None
        return

    @property
    def poller_configuration(self):
        """
        A PollerConfiguration object
        """
        if self._poller_configuration is None:
            self._poller_configuration = QueryConfiguration(configuration=self.configuration,
                                                           section=self.section_header)
        return self._poller_configuration

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
            name = 'CommandPoller'
            bold_name = bold + name + reset

            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- a threaded commands to csv creator '
            self._sections['Description'] = bold_name + ' stores the output of threaded commands as a csv'
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
        This is the CommandPoller product

        To allow repeated running the CommanPoller is created anew every time

        :precondition: self.configuration is a configuration map
        """
        kwargs = dict(self.configuration.items(section=self.section_header,
                                                   optional=False))
        self.logger.debug("Building the CommandPoller with: {0}".format(kwargs))

        connection_section = self.configuration.get(section=self.section_header,
                                                    option='connection')
        client = self.host_builder(connection_section)
        self._product = PollerBuilder(connection=client,
                                      configuration=self.query_configuration,
                                      storage=self.storage).product
        return self._product
        
    def fetch_config(self):
        """
        Prints example configuration to stdout
        """
        print CONFIGURATION
# end class CommandPoller
