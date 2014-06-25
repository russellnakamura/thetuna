
# python standard library
from collections import OrderedDict

# tuna
from component import BaseComponent
from tuna import ConfigurationError
from tuna.plugins.base_plugin import BasePlugin
from tuna.infrastructure import singletons
from tuna.parts.storage.nullstorage import NullStorage
from tuna.commands.iperf.iperf import IperfConfiguration, IperfClass
from tuna import GLOBAL_NAME
from tuna.hosts.host import TheHost, HostConfiguration


class IperfDataConstants(object):
    """
    Constants for builders of the XYData class
    """
    __slots__ = ()
    store_output_option = 'store_output'
    repetitions_option = 'repetitions'
    direction_option = 'direction'
    client_section_option = 'client_section'
    server_section_option = 'server_section'
    aggregator_option = 'aggregator'


CONFIGURATION = """
[IperfData]
# this follows the pattern for plugins --
# the header has to match what's in the Optimizers `components` list
# the component option has to be XYData
component = Iperf

# to shorten this section the configuration
# for the client (DUT) and server (Traffic PC)
# are broken out so you have to indicate their
# section names here (this is case-sensitive)
client_section = DUT
server_section = TPC

# if store output is set to true, save the raw iperf files
#store_output = True

# the iperf output has to be reduced to a single number
# the default is to take the median of all outputs
# for something else change it (only max, min, or sum for now)
#aggregator = sum

# direction can be anything that starts with 'u' (for upstream only)
# 'd' (downstream only), or 'b' (both)
# I have no idea how to interpret the best location if you measure both, though
# where upstream means DUT -> Server
# and downstream means SERVER -> DUT
direction = downstream

# iperf settings
# these can be any long-form iperf options (without the dashes)
# so looking at the iperf man page (or `iperf -h`) will give you the valid options
# note that in some cases iperf uses shortenings (e.g. `len` vs `length`)
# Any option not given will use the iperf defaults
parallel = 4

# if the option takes no settings, use True to turn on
# udp = True

# but note that udp doesn't work yet (only the client
# side is being used by the optimizers)
# also the --client <hostname> and --server options are set using the
# DUT and Server info so don't set them

[DUT]
# this is an example for the connection to the dut
# the section header has to match what's declared in the
# iperf section

# the connection can be ssh or telnet
connection_type = ssh
control_ip = 192.168.10.50
test_ip = 192.168.20.50
username = tester
# password is optional if host-keys are set up
# and you are using ssh
# password = testlabs
# the prefix will be appended to all commands sent to the device
# the main uses are adding 'adb shell' or path-directories
# because these two cases are different (`adb shell` is space separated from commands
# while setting a PATH has to be semi-colon separated) the prefix is added as-is
# it's up to the user to create a sensible one
# prefix = PATH=/opt/wifi:$PATH; adb shell

# timeout is amount of time to allow a command to run before giving up
# because timeouts cause an error, this should only be used for problematic
# devices
# timeout = 1 minute 30 seconds

# operating-system is just an identifier currently
# operating_system = linux

# I only used the subset of parameters that I thought necessary
# if you need to add one and you know it's supported by
# paramiko or telnet you should be able to add it
# e.g. if you know there is a 'port' parameter you can set it:
# port = 52686

[TPC]
# this is basically configured the same way as the client-section
connection_type = ssh
control_ip = 192.168.10.50
test_ip = 192.168.20.50
username = tester
"""

DESCRIPTION = """
The Iperf quality metric runs iperf and returns the median bandwidth to the optimizer that calls it. Note that if you run it without interval (--interval) reporting it will grab the summary value at the end which, I believe is the mean and might be slightly different from a mean of interval reporting. I don't know which is more accurate but I assume the final calculation is.
"""


FILE_FORMAT = "iperf_input_{inputs}_rep_{repetition}_{direction}"

class IperfMetric(BaseComponent):
    """
    An aggregator of iperf output
    """
    def __init__(self, directions, iperf, repetitions=1, aggregator=None):
        """
        IperfMetric constructor

        :param:

         - `repetititons`: number of times to repeat iperf test
         - `directions`: iterable collection of iperf directions
         - `iperf`: a built IperfClass object
         - `aggregator`: callable to reduce iperf outputs to one value
        """        
        self.repetitions = repetitions
        self.directions = directions
        self.iperf = iperf
        self._aggregator = aggregator
        return

    @property
    def aggregator(self):
        """
        callable to reduce multiple outputs to one value
        """
        if self._aggregator is None:
            self._aggregator = numpy.median            
        return self._aggregator

    def __call__(self, target):
        """
        The main interface returns aggregate value for iperf output

        :param:

         - `target`: object with `inputs` and `output`
        """
        outcomes = []
        if target.output is None:
            for repetition in xrange(self.repetitions):
                for direction in self.directions:
                    filename = FILE_FORMAT.format(repetition=repetition,
                                                  direction=direction,
                                                  inputs="_".join([str(item) for item in target.inputs]))
                    outcomes.append(self.iperf(direction, filename))
            target.output = self.aggregator(outcomes)
        return target.output

    def check_rep(self):
        """
        Checks the given constructor parameters
        """
        assert type(self.repetitions) is IntType
        assert self.repetitions > 0
        assert len(self.directions) > 0
        assert hasattr(self.aggregator, '__call__')
        return

    def close(self):
        """
        This doesn't do anything
        """
        return
# end IperfMetric            


class Iperf(BasePlugin):
    """
    Builds IperfMetric objects from configuration-maps
    """
    def __init__(self, *args, **kwargs):
        """
        Iperf constructor

        :param:

         - `configuration`: configuration map
         - `section`: name of section with needed options
        """
        super(Iperf, self).__init__(*args, **kwargs)
        self._client = None
        self._server = None
        self._storage = None
        self._iperf = None
        self._iperf_configuration = None
        return

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
    def server(self):
        """
        Host object for the traffic-PC
        """
        if self._server is None:
            section = self.configuration.get(section=self.section_header,
                                             option=IperfDataConstants.server_section_option,
                                             optional=True)
            self._server = self.host_builder(section)
        return self._server
        
    @property
    def client(self):
        """
        Host object for the DUT
        """
        if self._client is None:
            section = self.configuration.get(section=self.section_header,
                                                    option=IperfDataConstants.client_section_option,
                                                    optional=False)
            self._client = self.host_builder(section)
        return self._client

    @property
    def storage(self):
        """
        storage object (file or null)
        """
        if self._storage is None:
            store_output = self.configuration.get_boolean(section=self.section_header,
                                                          option=IperfDataConstants.store_output_option,
                                              optional=True,
                                              default=False)
            if store_output:
                self._storage = singletons.get_filestorage(name=GLOBAL_NAME)
            else:
                self._storage = NullStorage()
        return self._storage

    @property
    def iperf_configuration(self):
        """
        Iperf configuration object
        """
        if self._iperf_configuration is None:
            self._iperf_configuration  = IperfConfiguration(configuration=self.configuration,
                                                            section=self.section_header)
        return self._iperf_configuration
    
    @property
    def iperf(self):
        """
        iperf class object
        """
        if self._iperf is None:
            self._iperf = IperfClass(dut=self.client,
                                     traffic_server=self.server,
                                     client_settings=self.iperf_configuration.client_settings,
                                     server_settings=self.iperf_configuration.server_settings,
                                     storage=self.storage)
        return self._iperf
    
    @property
    def product(self):
        """
        A built Iperf object
        """
        if self._product is None:            
            repetitions = self.configuration.get_int(section=self.section_header,
                                                 option=IperfDataConstants.repetitions_option,
                                                 optional=True,
                                                 default=1)

            directions = self.iperf_configuration.direction
            if directions.startswith('b'):
                directions = 'upstream downstream'.split()

            else:
                directions = [directions]
            aggregator = self.configuration.get(section=self.section_header,
                                                option=IperfDataConstants.aggregator_option,
                                                optional=True)
            if aggregator is not None:
                aggregators = dict(zip("min max sum".split(), [min, max, sum]))
                aggregator = aggregators[aggregator.lower()]
            self._product = IperfMetric(repetitions=repetitions,
                                   directions=directions,
                                   iperf=self.iperf,
                                   aggregator=aggregator)
        return self._product

    @property
    def sections(self):
        """
        An ordered dictionary for the HelpPage
        """
        if self._sections is None:
            bold = '{bold}'
            reset = '{reset}'
            name = 'Iperf'
            bold_name = bold + name + reset

            self._sections = OrderedDict()
            self._sections['Name'] = '{blue}' + name + reset + ' -- A component for optimizer plugins'
            self._sections['Description'] = bold_name + DESCRIPTION
            self._sections["Configuration"] = CONFIGURATION
            self._sections['Files'] = __file__
        return self._sections

    def fetch_config(self):
        """
        prints sample configuration to the scree
        """
        print CONFIGURATION
        return

