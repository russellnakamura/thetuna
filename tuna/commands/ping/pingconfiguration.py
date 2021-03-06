
# this package
from tuna.infrastructure.baseconfiguration import BaseConfiguration
from tuna.commands.ping.ping import PingConstants


class PingConfiguration(BaseConfiguration):
    """
    A class to hold configuration for the ping
    """
    def __init__(self, *args, **kwargs):
        """
        PingConfiguration constructor
        """
        super(PingConfiguration, self).__init__(*args, **kwargs)
        self._target = None        
        self._time_limit = None
        self._threshold = None
        self._arguments = None
        self._operating_system = None
        self._timeout = None
        self._data_expression = None
        self._trap_errors = None
        return

    @property
    def target(self):
        """
        The address or hostname to ping
        """
        if self._target is None:
            self._target = self.configuration.get(section=self.section,
                                                  option=PingConfigurationConstants.target,
                                                  optional=True)
        return self._target

    @target.setter
    def target(self, new_target):
        """
        sets the ping target

        :param:

         - `new_target`: address to ping (or None)
        """
        self._target = new_target
        return
    
    @property
    def time_limit(self):
        """
        The number of seconds to try to ping the target
        """
        if self._time_limit is None:
            self._time_limit = self.configuration.getfloat(section=self.section,
                                                           option=PingConfigurationConstants.time_limit,
                                                           optional=True,
                                                           default=PingConfigurationConstants.default_time_limit)
        return self._time_limit

    @property
    def threshold(self):
        """
        Number of consecutive pings to consider a success
        """
        if self._threshold is None:
            self._threshold = self.configuration.getint(section=self.section,
                                                        option=PingConfigurationConstants.threshold,
                                                        optional=True,
                                                        default=PingConfigurationConstants.default_threshold)
        return self._threshold

    @property
    def arguments(self):
        """
        String of arguments for the ping command (uses linux as default)
        """
        if self._arguments is None:
            self._arguments = self.configuration.get(section=self.section,
                                                     option=PingConfigurationConstants.arguments,
                                                     optional=True,
                                                     default=PingConstants.linux_one_repetition)
        return self._arguments

    @property
    def operating_system(self):
        """
        The operating system used to chose the form of the ping command
        """
        if self._operating_system is None:
            self._operating_system = self.configuration.get(section=self.section,
                                                            option=PingConfigurationConstants.operating_system,
                                                            optional=True,
                                                            default=PingConfigurationConstants.default_os)
        return self._operating_system

    @property
    def timeout(self):
        """
        The readline timeout for the connection
        """
        if self._timeout is None:
            self._timeout = self.configuration.getfloat(section=self.section,
                                                        option=PingConfigurationConstants.timeout,
                                                        optional=True,
                                                        default=PingConfigurationConstants.default_timeout)
        return self._timeout

    @property
    def data_expression(self):
        """
        A regular expression to match a successful ping
        """
        if self._data_expression is None:
            self._data_expression = self.configuration.get(section=self.section,
                                                           option=PingConfigurationConstants.data_expression,
                                                           optional=True,
                                                           default=PingConfigurationConstants.default_data_expression)
        return self._data_expression

    @property
    def trap_errors(self):
        """
        Boolean to indicate if socket errors should be fatal or not
        """
        if self._trap_errors is None:
            self._trap_errors = self.configuration.getboolean(section=self.section,
                                                              option=PingConfigurationConstants.trap_errors,
                                                              optional=True,
                                                              default=PingConfigurationConstants.default_trap_errors)
        return self._trap_errors
    
    
    @property
    def example(self):
        """
        An example configuration string
        """
        return """
#[{section}]
# 'target' (default: None) is the IP address or name to ping (RVR will use the traffic server if not given)
# {t} = www.google.com

# 'time_limit'  is number of seconds to try to ping before giving up
# time_limit = {time_limit}

# 'threshold' is the number of consecutive pings needed for a success
# threshold = {threshold}

# 'arguments' are the arguments to give the ping command
# arguments = {args}

# 'operating_system' is used to chose the arguments for the ping
# operating_system = {os}

# 'timeout' is the seconds to wait for socket readlines (try to keep above 1 second)
# timeout = {timeout}

# 'data_expression' is the regular expression to extract the round-trip time (used to check success)
# data_expression = {dexpression}

# 'trap_errors'  if False, will raise an error if there is a socket error
# otherwise it will just log it
#trap_errors = {dtrap}""".format(section=self.section,
                                 t=PingConfigurationConstants.target,
                               time_limit=PingConfigurationConstants.default_time_limit,
                               threshold=PingConfigurationConstants.default_threshold,
                               args=PingConstants.linux_one_repetition,
                               os=PingConfigurationConstants.default_os,
                               timeout=PingConfigurationConstants.default_timeout,
                               dexpression=PingConfigurationConstants.default_data_expression,
                               dtrap=PingConfigurationConstants.default_trap_errors)

    @property
    def section(self):
        """
        The name for this section in the configuration file
        """
        if self._section is None:
            self._section = PingConfigurationConstants.section
        return self._section
    
    def check_rep(self):
        """
        Check the representation for inconsistancies
        """
        super(PingConfiguration, self).check_rep()
        return

    def reset(self):
        """
        Reset the values to None
        """
        self._target = None
        self._time_limit = None
        self._threshold = None
        self._arguments = None
        self._operating_system = None
        self._timeout = None
        self._data_expression = None
        self._trap_errors = None
        return
# end class PingConfiguration    


class PingConfigurationConstants(object):
    """
    Holder of constant values for PingConfiguration
    """
    __slots__ = ()
    section = 'ping'

    # options
    data_expression = 'data_expression'
    trap_errors = 'trap_errors'
    timeout = 'timeout'
    operating_system = 'operating_system'
    arguments = 'arguments'
    threshold = 'threshold'
    time_limit = 'time_limit'
    target = 'target'

    # defaults
    default_trap_errors = True
    default_timeout = 10
    default_data_expression = None
    default_os = None
    default_threshold = 5
    default_time_limit = 300
# end PingConfigurationConstants    
