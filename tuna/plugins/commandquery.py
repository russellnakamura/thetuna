
# python standard library
from collections import OrderedDict

# this package
from tuna.infrastructure import singletons
from tuna import GLOBAL_NAME
from base_plugin import BasePlugin
from tuna.parts.storage.storageadapter import StorageAdapter
from tuna.hosts.host import TheHost, HostConfiguration

from tuna.commands.query import QueryBuilder, QueryConfiguration


in_pweave = __name__ == '__builtin__'


SECTION = 'CommandQuery'
CONFIGURATION = """
[{section}]
# the section-name has to match an option in the TUNA section
# the plugin has to be the actual class name
plugin = CommandQuery

# the connection should be the name of a section in the config
# that has information to setup a connection to the device
connection = DUT

# these are arbitrary commands that will be called in between attenuations
# it's original use-case is to get RSSI and other monitoring information
# but since it's free-form you can pass in whatever you like

# delimiter refers to what separates the command and the expression
# this is provided so that if the command or expression has a comma in it
# you can use an alternative

#delimiter =  ,

# if you want to specify a filename set the filename option
# filename = data.csv

# to change the readline timeout
# timeout = 5

# to have it crash instead of trap socket errors
# trap_errors = False

# everything else is of the format:
# <column-header> = <command><delimiter><regular expression>
# the column-header will be used in the csv-file
# the regular expression has to have a group '()' or it will raise an error
            
#rssi = iwconfig wlan0,Signal\slevel=(-\d+\sdBm)
#noise = wl noise, (.*)
#bitrate = iwconfig wlan0, Bit\sRate=(\d+\.\d\sMb/s)
#counters = wl counters, (rxcrsglitch [0-9]* )
""".format(section=SECTION)


output_documentation = __name__ == '__builtin__'


class CommandQuery(BasePlugin):
    """
    A command to csv-file plugin
    """
    def __init__(self, *args, **kwargs):
        """
        CommandQuery plugin Constructor

        """
        super(CommandQuery, self).__init__(*args, **kwargs)
        self._storage = None
        self._query_configuration = None
        return

    @property
    def query_configuration(self):
        """
        A QueryConfiguration object
        """
        if self._query_configuration is None:
            self._query_configuration = QueryConfiguration(configuration=self.configuration,
                                                           section=self.section_header)
        return self._query_configuration

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
            name = 'CommandQuery'
            bold_name = bold + name + reset

            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- a commands to csv creator '
            self._sections['Description'] = bold_name + ' stores the output of commands as a csv'
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
        This is the CommandQuery product

        To allow repeated running the CommandDump is created anew every time

        :precondition: self.configuration is a configuration map
        """
        kwargs = dict(self.configuration.items(section=self.section_header,
                                                   optional=False))
        self.logger.debug("Building the CommandQuery with: {0}".format(kwargs))

        connection_section = self.configuration.get(section=self.section_header,
                                                    option='connection')
        client = self.host_builder(connection_section)
        self._product = QueryBuilder(connection=client,
                                     configuration=self.query_configuration,
                                     storage=self.storage).product
        return self._product
        
    def fetch_config(self):
        """
        Prints example configuration to stdout
        """
        print CONFIGURATION
# end class CommandQuery
