
# python standard library
from collections import namedtuple
import os
import time
import threading
import textwrap
import curses.ascii

# third party
import numpy

# this package
from tuna import BLUE_BOLD_RESET
from tuna import BaseClass, TunaError
from iperfsettings import IperfConstants, IperfServerSettings, IperfClientSettings
from iperfexpressions import HumanExpression, CsvExpression
from iperfparser import IperfParser
from tuna.parts.storage.file_writer import LogWriter, TimestampWriter
from tuna.infrastructure.baseconfiguration import BaseConfiguration
from tuna import ConfigurationError
from tuna.parts.eventtimer import EventTimer


UNDERSCORE = '_'
WRITEABLE = 'w'
IPERF = 'iperf {0}'
CLIENT_PREFIX = 'client_'
SERVER_PREFIX = 'server_'
TIMESTAMP = '{timestamp}'


ClientServer = namedtuple('ClientServer', 'client server'.split())


class IperfClass(BaseClass):
    """
    A runner of iperf tests
    """
    def __init__(self, dut, traffic_server, client_settings,
                 server_settings, storage, parser=None, aggregator=None):
        """
        IperfClass Constructor

        :param:

         - `dut`: something that implements a HostSSH-like interface to the DUT
         - `traffic_server`: HostSSH-like interface to traffic server
         - `client_settings`: IperfClientSettins instance
         - `server_settings: an IperfServerSettings instance
         - `storage`: File-like object to write output to
         - `parser`: parser to extract numeric values from the lines
         - `aggregator`: callable to reduce parser.intervals.values() to a number
        """
        super(IperfClass, self).__init__()
        self.dut = dut
        self.traffic_server = traffic_server
        self.client_settings = client_settings
        self.server_settings = server_settings
        self.storage = storage
        self._client_server = None
        self._udp = None
        self._event_timer = None
        self.stop = False
        self._parser = parser
        self._aggregator = aggregator
        self.aggregated_value = None
        return

    @property
    def aggregator(self):
        """
        callable to reduce the parsed values to a number (median by default)
        """
        if self._aggregator is None:
            self._aggregator = numpy.median
        return self._aggregator

    @property
    def event_timer(self):
        """
        An event-timer instance to help the server block the client
        """
        if self._event_timer is None:
            try:
                self._event_timer = EventTimer(seconds=self.server_settings.sleep)
            except AttributeError as error:
                self.logger.debug('server_settings.sleep not given, using 1 second')
                self._event_timer = EventTimer(seconds=1)
        return self._event_timer

    @property
    def client_server(self):
        """
        A dict with {direction:ClientServer} named tuples
        """
        if self._client_server is None:
            self._client_server = {IperfConstants.down:ClientServer(client=self.traffic_server,
                                                                                 server=self.dut),
                                    IperfConstants.up:ClientServer(client=self.dut,
                                                               server=self.traffic_server)}
        return self._client_server

    @property
    def udp(self):
        """
        A check for the UDP flag in the settings

        :return: boolean if this is a UDP session
        :raise: TunaError if one setting has UDP and the other doesn't
        """
        if self._udp is None:
            # empty strings resolve to False so a boolean check is needed
            state = (self.client_settings.get('udp') is not None,
                     self.server_settings.get('udp') is not None)
            self._udp = any(state)
            if self._udp and not all(state):
                raise TunaError("Conflicting settings- Client: {0}, Server: {1}".format(self.client_settings.get('udp'),
                                                                                              self.server_settings.get('udp')))
        return self._udp
        
    def __call__(self, direction, filename):
        """
        the main interface

        :param:

         - `direction`: IperfConstants.up or IperfConstants.down (probably 'downstream' or 'upstream')
         - `filename`: path to use as basis for filename

        :return: aggregated value (assumes side-effect of self.run is to set self.aggregated_value)
        """
        if direction.startswith('d'):
            self.logger.info("'{0}' Server --> DUT".format(direction))
        elif direction.startswith('u'):
            self.logger.info("'{0}' DUT --> Server".format(direction))
        # get the client and server for the given directon
        client_server = self.client_server[direction]

        # this could be done with tuple-unpacking but I'm trying to get rid of ordering mix-ups
        client, server = client_server.client, client_server.server
        
        # try to kill all the iperf sessions
        self.logger.info(BLUE_BOLD_RESET.format("** Killing Iperf Processes **"))
        client.kill_all('iperf')
        server.kill_all('iperf')

        # add the direction and protocol to the filename
        if self.udp:
            protocol = 'udp'
            self.logger.info('UDP: Screen output will be from the server')
        else:
            protocol = 'tcp'
            self.logger.info('TCP: Screen output will be from the client')
        directory, filename = os.path.split(filename)
        filename = os.path.join(directory, UNDERSCORE.join([direction,
                                                            TIMESTAMP,
                                                            protocol, filename]))

        # set the server as the target for the client in the settings
        self.client_settings.server = server.testInterface

        # run the server and client
        self.logger.info(BLUE_BOLD_RESET.format("** Starting the Server **"))
        self.start_server(server, filename)
        self.logger.info(BLUE_BOLD_RESET.format("** Starting the Client **"))
        self.run_client(client, filename)

        # for telnet, you can't send more input while the server is running
        # you can run it in daemon mode, but then UDP output won't show up
        # so, until a better idea comes up, I'm closing the server's connection
        self.logger.info("Closing the connection ({0}) so interactive connections won't block input".format(server))

        # there seems to be a race condition with the telnet client running in a thread and the closing of the server
        self.stop = True
        server.close()
        #time.sleep(1)
        return self.aggregated_value

    def downstream(self, filename):
        """
        This is slightly safer than using the call, since you don't need to know the direction string

        (but underneath it all it uses __call__)

        :param:

         - `filename`: path to use as basis for output file
        """
        self(IperfConstants.down, filename)
        return

    def upstream(self, filename):
        """
        Like `downstream` this is just a convenience pass-through to __call__

        :param:

         - `filename`: path to use as basis for iperf output file
        """
        self(IperfConstants.up, filename)
        return

    @property
    def parser(self):
        """
        an iperf parser (this has to be reset if it's re-used)
        """
        if self._parser is None:
            interval = 10
            threads = 1
            if self.client_settings.get('interval') is not None:
                interval = self.client_settings.get('interval')
            elif self.client_settings.get('time') is not None:
                interval = self.client_settings.get('time')

            if self.client_settings.get('parallel') is not None:
                threads = self.client_settings.get('parallel')
            self._parser =  IperfParser(expected_interval=interval,
                                        threads=threads)
        return self._parser

        
    def run(self, host, settings, filename, verbose=True, timeout=10):
        """
        Runs one-direction of traffic

        :param:

         - `host`: HostSSH or paramiko-like object
         - `settings`: something whose __str__ resolves to iperf parameters
         - `filename`: name to save raw output to
         - `verbose`: if True, emit output as it appears
         - `timeout`: readline timeout -- set to None for servers or it will raise an error

        :raise: socket.timeout if the readline timeout is exceeded
        """
        self.stop = False
        with self.storage.open(filename) as opened:
            if self.client_settings.parallel > 1:
                expression = "SUM|,-1,"
            elif self.client_settings.reportstyle is None:
                expression = HumanExpression.regex
            else:
                expression = CsvExpression.regex

            if verbose:
                logger = self.logger.info
            else:
                logger = self.logger.debug

            timestamper = TimestampWriter(open_file=opened)
            writer = LogWriter(logger=logger,
                               open_file=timestamper,
                               expression=expression)
            parser = self.parser
            
            command = IPERF.format(settings)
            self.logger.info(command)

            stdin, stdout, stderr = host.exec_command(command, timeout=timeout)

            for line in stdout:
                self.logger.debug(line)
                if self.stop:
                    return
                writer.write(line)
                if verbose:
                    parser(line)
                
            for line in stderr:
                if line:
                    # the killing of the server is causing this to dump errors
                    # so it's changed to debug until a solution is found
                    self.logger.debug("Iperf.run ({0}) error: {1}".format(settings, line))
                    
            if verbose:
                self.aggregated_value = self.aggregator(parser.intervals.values())
                # verbose means this is the side we care about (client for TCP, server for UDP)
                self.logger.info("Aggregated Iperf Value ({1}): {0}".format(self.aggregated_value,
                                                                            self.aggregator.__name__))
                parser.reset()
        return 

    def start_server(self, server, filename):
        """
        Starts the server in a thread so the client can run.

        :param:

         - `server`: paramiko-like thing to run iperf on
         - `filename`: base-name for the file to save the raw output

        :postcondition: self.server_thread is a thread with self.run running
        """
        # add a prefix to identify the file
        path, filename = os.path.split(filename)
        filename = os.path.join(path, SERVER_PREFIX + filename)

        # start the thread
        self.server_thread = threading.Thread(target=self.run,
                                              name='server_thread',
                                              kwargs={'host':server,
                                                      'settings':self.server_settings,
                                                      'filename':filename,
                                                      'verbose':self.udp,
                                                      'timeout':None})
        self.server_thread.daemon = True
        self.server_thread.start()

        # block run_client for a short time
        self.event_timer.clear()
        return

    def run_client(self, client, filename):
        """
        Runs the client iperf session

        :param:

         - `client`: paramiko.SSHClient like object
         - `filename`: name to save output to

        :precondition: self.client_settings.server is set to the server hostname
        """
        path, filename = os.path.split(filename)
        filename = os.path.join(path, CLIENT_PREFIX + filename)

        # run it
        self.event_timer.wait()
        # for slow connections (especially on telnet and serial -- the timeout has to be longer than the interval)
        # but sometimes the user doesn't set it -- so this has gotten convoluted
        # why doesn't everyone implement ssh?
        # this is going to be very aggresive with the timeouts
        # the last option (10) is the default for iperf
        #timeout = max(self.client_settings.get('interval'),
        #              self.client_settings.get('time'), 10) * 2
        interval =  self.client_settings.get('interval')
        if interval is not None:
            timeout = interval * 4
        else:
            timeout = max(self.client_settings.get('time'), 10) *1.5
        self.logger.info("Setting client's readline timeout to {0} seconds".format(timeout))
        self.run(host=client, filename=filename,
                 settings=self.client_settings,
                 timeout=timeout,
                 verbose=not self.udp)
        return

    def version(self, connection):
        """
        Runs iperf with the version flag

        :return: whatever iperf outputs
        """
        stdin, stdout, stderr = connection.exec_command(IPERF.format('--version'))

        output = "".join([line for line in stdout])
        error = ''.join([line for line in stderr])
        if error:
            output += " {0}".format(error)
        return output
# end class IperfClass


class IperfEnum(object):
    """
    Iperf constants
    """
    __slots__ = ()
    section = 'iperf'
    old_section = 'traffic'
    false = 'off no false'.split()

    # options
    direction = 'direction'
    upstream = 'upstream'
    downstream = 'downstream'
    both = 'both'

    # defaults
    default_direction = both


EXAMPLE =  textwrap.dedent("""
[Iperf]
# these are iperf options
# directions can be upstream, downstream or both (default : {direction})
# actually only checks the first letter so could also be ugly, dumb, or bunny too
direction = upstream

# everything else uses iperf long-option-names
# to get a list use `man iperf`
# the left-hand-side options are the iperf options without --
# for example, to set --parallel:
#parallel = 5

# if the flag takes no options, use True to set
#udp = True

# --client <hostname> and server are set automatically don't put them here
# put all the other settings in, though, and the client vs server stuff will get sorted out
""".format(direction=IperfEnum.default_direction))

class IperfConfiguration(BaseConfiguration):
    """
    A holder of iperf parameters
    """
    def __init__(self, section=None, *args, **kwargs):
        """
        IperfConfiguration constructor

        :param:

         - `configuration`: configuration adapter with iperf parameters
         - `section`: name of section with options
        """
        super(IperfConfiguration, self).__init__(*args, **kwargs)
        self._section = section
        self._direction = None
        self._client_settings = None
        self._server_settings = None
        self.exclusions.append('assert_in')
        return

    @property
    def example(self):
        """
        :return: example iperf configuration
        """
        if self._example is None:
            self._example = EXAMPLE
        return self._example

    @property
    def section(self):
        """
        The section name in the configuration
        """
        if self._section is None:
            self._section = IperfEnum.section
        return self._section

    @property
    def direction(self):
        """
        Gets the traffic direction (only uses the first letters (u, d, or b))

        :section: traffic
        :option: direction
        :return: upstream, downstream, both
        :raise: TunaError if direction doesn't start with valid letter
        """
        if self._direction is None:
            direction = self.configuration.get(section=self.section,
                                               option=IperfEnum.direction,
                optional=True,
                default=IperfEnum.default_direction)
            if direction.lower().startswith('u'):
                self._direction = IperfEnum.upstream
            elif direction.lower().startswith('d'):
                self._direction = IperfEnum.downstream
            elif direction.lower().startswith('b'):
                self._direction = IperfEnum.both
            else:
                self.logger.error("[traffic] direction={0}".format(direction))
                raise TunaError("Unknown traffic direction: {0}".format(direction))
        return self._direction

    @property
    def client_settings(self):
        """
        An IperfClientSettings object

        :return: IperfClientSettings built from the configuration
        """
        if self._client_settings is None:
            self._client_settings = IperfClientSettings()
            parameters = self.get_section_dict()
            self._client_settings.update(parameters)
        return self._client_settings

    @property
    def server_settings(self):
        """
        IperfServerSettings
        """
        if self._server_settings is None:
            parameters = self.get_section_dict()
            self._server_settings = IperfServerSettings()
            self._server_settings.update(parameters)
        return self._server_settings

    def get_section_dict(self):
        """
        Convenience method to get the section dict

        :return: section-dictionary for this section
        """
        try:
            parameters = dict(self.configuration.items(self.section))
        except ConfigurationError as error:
            print "exception caught"
            self.logger.debug(error)

            # try the old one
            parameters = dict(self.configuration.items(IperfEnum.old_section))

        # python resolves all strings to True
        # try to keep the user from shooting himself in the foot
        # '0' is not allowed in this case, just 'no', 'false', and 'off'
        for key, value in parameters.iteritems():            
            if value.lower() in IperfEnum.false:
                parameters[key] = False
        return parameters


    def reset(self):
        """
        Sets the properties to None
        """
        self._direction = None
        self._client_settings = None
        self._server_settings = None
        return

    def check_rep(self):
        """
        Checks the representation
        """
        super(IperfConfiguration, self).check_rep()
        return
# end IperfConfiguration
