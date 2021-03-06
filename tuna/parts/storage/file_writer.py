
# python standard library
import datetime
import re
now = datetime.datetime.now


class TimestampWriter(object):
    """
    A class to add timestamps to lines being written to files
    """
    def __init__(self, open_file):
        """
        TimestampWriter constructor

        :param:

         - `open_file`: a file opened for writing
        """
        self.open_file = open_file
        return

    def write(self, line):
        """
        Adds a timestamp and writes the line to the open_file

        :param:

         - `line`: string to write to output
        """
        self.open_file.write('{0},{1}'.format(now().isoformat(), line))
        #self.open_file.write(line)
        return
# end TimestampWriter        


class LogWriter(object):
    """
    A writer to a log and a file
    """
    def __init__(self, logger, open_file, expression=None):
        """
        LogWriter Constructor

        :param:

         - `logger`: a callable writer (e.g. logger.info (not the logger by itself))
         - `open_file`: something that looks like a writeable file
         - `expression`: an (uncompiled) regular expression to match the lines to log
        """
        self.logger = logger
        self.open_file = open_file
        self._expression = None
        self.expression = expression
        return

    @property
    def expression(self):
        """
        compiled regular expression to match lines to write
        """
        if self._expression is None:
            self._expression = re.compile(".*")
        return self._expression

    @expression.setter
    def expression(self, regex):
        """
        sets the expression

        :param:

         - `regex`: string regular expression to match lines to be logged
        """
        if regex is not None:
            self._expression = re.compile(regex)
        else:
            self._expression = regex
        return

    def write(self, line):
        """
        Logs the line and writes to file
        """
        if self.expression.search(line):
            self.logger(line.rstrip('\n'))
        #self.open_file.write("{0},{1}".format(now().isoformat(), line))
        self.open_file.write(line)
        return
# end class LogWriter    
