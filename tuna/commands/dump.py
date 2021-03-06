
# python standard library
import socket
import textwrap
import datetime

# this package
from tuna import BaseComponent, TunaError
from tuna.clients.clientbase import suppresssocketerrors
from tuna import LOG_TIMESTAMP


WRITEABLE = 'w'


class DumpConstants(object):
    """
    Constants for the Dump
    """
    __slots__ = ()
    # defaults
    default_timeout = 5
    default_identifier = 'dump'
    default_mode = WRITEABLE

    # options
    timeout = 'timeout'
    
    example = textwrap.dedent("""
#[dump]
# comment this section out if you don't want a dump
    
# to change it use the timeout option
# timeout = {time}

# for the commands you should use the form:
# <identifier_1> = <command_1>

# the identifiers can be anything as long as each is unique
# the command should be the actual string you want to send to the device
# as an example for 'dmesg':
# dump = dmesg -k
    """.format(time=default_timeout))
    
# end DumpConstants    


class TheDump(BaseComponent):
    """
    The Dump dumps the output of a command to a file
    """
    def __init__(self, command, connection, storage,
                 identifier=None, filename=None,
                 timeout=DumpConstants.default_timeout, mode=WRITEABLE):
        """
        TheDump's Constructor

        :param:

         - `command`: the command (string) to send to the device to get output
         - `identifier`: string to identify this object
         - `connection`: connection to the device with an `exec_command` method
         - `storage`: File-like object to dump output to
         - `filename`: Name for output file
         - `timeout`: Readline timeout (seconds)
         - `mode`: mode for the file ('w' or 'a')
        """
        super(TheDump, self).__init__()
        self._identifier = identifier
        self.command = command
        self.connection = connection
        self.timeout = timeout
        self._filename = filename
        self.storage = storage
        self.mode = mode
        return

    @property
    def identifier(self):
        """
        String to identify this dump
        """
        if self._identifier is None:
            self._identifier = DumpConstants.default_identifier
        return self._identifier

    @property
    def filename(self):
        """
        Name to use for file to dump command output to

        If not set by user uses '<host-str>_<identifier>_<command 1st token>.txt'

        :rtype: StringType
        :return: filename for output
        """
        if self._filename is None:
            connection_name = self.connection.hostname
            self._filename = "{0}_{1}_{2}.txt".format(connection_name,
                                                      self.identifier,
                                                      self.command.split()[0])
        return self._filename

    @suppresssocketerrors
    def __call__(self):
        """
        runs the command and saves it to the file
        """
        with self.storage.open(self.filename, mode=self.mode) as output_file:
            stdin, stdout, stderr = self.connection.exec_command(self.command,
                                                                 timeout=self.timeout)
            for line in stdout:
                #timestamp = datetime.datetime.now().strftime(LOG_TIMESTAMP)
                #output_file.write("{0},{1}".format(timestamp,
                #                                   line))
                output_file.write(line)
                
            for line in stderr:
                if line:
                    self.logger.error(line)
        return

    def close(self):
        """
        Does nothing at the moment
        """
        return

    def check_rep(self):
        """
        Does nothing at the moment
        """
        return

    def __str__(self):
        return "{0}: {1}".format(self.identifier, self.command)
# end class TheDump    
