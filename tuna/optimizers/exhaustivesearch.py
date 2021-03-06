
# python standard library
import datetime

# third party
import numpy

# this package
from tuna.components.component import BaseComponent
from tuna import ConfigurationError
from tuna.parts.xysolution import XYSolution
from tuna import LOG_TIMESTAMP


class ExhaustiveSearchConstants(object):
    __slots__ = ()
    # configuration options
    minima_option = 'minima'
    maxima_option = 'maxima'
    increments_option = 'increments'
    datatype_option = 'datatype'


class ExhaustiveSearch(BaseComponent):
    """
    An exhaustive grid searcher
    """    
    def __init__(self, minima, maxima, increments, quality, solutions,
                 observers=None):
        """
        ExhaustiveSearch constructor

        :param:

         - `minima`: array of lowest-values for coordinates
         - `maxima`: array of maximum-values for coordinates
         - `increment`: array of step-sizes for coordinate-changes
         - `quality`: Object to assess quality of candidate solution
         - `observers`: composite of objects to get the best solution
         - `solutions`: object to write output to
        """
        super(ExhaustiveSearch, self).__init__()
        self.minima = minima
        self.maxima = maxima
        self.increments = increments
        self.quality = quality
        self.observers = observers
        self.solutions = solutions
        return

    def check_rep(self):
        """
        Checks the minima, maxima and increments

         * minima <= maxima
         * minima, maxmia, increments same dimension

        :raise: ConfigurationError if not valid
        """
        if not all(self.maxima >= self.minima):
            raise ConfigurationError("maxima ({0}) must be >= minima ({1})".format(self.maxima,
                                                                                   self.minima))
        if len(self.minima) != len(self.maxima):
            raise ConfigurationError(("Dimension Mismatch: minima"
                                      " {0}, maxima {1}").format(len(self.minima),
                                                                     len(self.maxima)))

        if len(self.maxima) != len(self.increments):
            raise ConfigurationError(("Dimension Mismatch: maxima"
                                      " {0}, increments {1}").format(len(self.maxima),
                                                                     len(self.increments)))
        return

    def close(self):
        """
        Does nothing
        """
        return

    def carry(self, candidate):
        """
        Carries the column values if they exceed maxima

        :return: candidate with values carried-over
        """
        last_column = len(candidate) - 1
        for column in xrange(len(candidate)):
            if candidate[column] > self.maxima[column]:
                candidate[column] = self.minima[column]
                if column != last_column:
                    candidate[column+1] += self.increments[column+1]
        return candidate
        

    def __call__(self):
        """
        Starts the search

        :return: best value found
        """
        candidate = XYSolution(self.minima.copy())
        increment = numpy.zeros(len(candidate))
        increment[0] = self.increments[0]

        candidate.inputs -= increment
        best = candidate.copy()
        self.log_info("Initial Best Solution: {0}".format(best))
        
        self.solutions.write("Time,Solution\n")
        #timestamp = datetime.datetime.now().strftime(LOG_TIMESTAMP)
        #output = "{0},1,{1}\n".format(timestamp, candidate)
        #self.solutions.write(output)
        
        while not numpy.array_equal(candidate.inputs, self.maxima):           
            candidate.inputs = self.carry(candidate.inputs + increment)
            candidate.output = None

            self.logger.debug("Trying candidate: {0}".format(candidate))

            if self.quality(candidate) > self.quality(best):
                timestamp = datetime.datetime.now().strftime(LOG_TIMESTAMP)
                output = "{0},{1}\n".format(timestamp,
                                            candidate)
    
                self.log_info("New Best Solution: {0}".format(output))
                best = candidate.copy()
                
            # record the path
            timestamp = datetime.datetime.now().strftime(LOG_TIMESTAMP)
            output = "{0},{1}\n".format(timestamp,
                                        candidate)

            self.logger.debug("Candidate Outcome: {0}".format(candidate))
            self.solutions.write(output)                
        self.log_info("Quality Checks: {0} Solution: {1} ".format(self.quality.quality_checks,
                                                                     best))
        if self.observers is not None:
            self.log_info("ExhaustiveSearch giving solution to '{0}'".format(self.observers))
            self.observers(target=best)
        return best
# end ExhaustiveSearch    


class ExhaustiveSearchBuilder(object):
    """
    A builder of ExhaustiveSearch objects
    """
    def __init__(self, configuration, section_header, quality, observers, solution_storage):
        """
        ExhaustiveSearchBuilder constructor

        :param:

         - `configuration`: ConfigurationMap with section for ExhaustiveSearch
         - `section_header`: section name in configuration with relevant options
         - `quality`: A callable object to assess quality of a candidate solution
         - `observers: callable to send best-solution to
         - `solution_storage`: writeable object to send output to
        """
        self.configuration = configuration
        self.section_header = section_header
        self._product = None
        self.quality = quality
        self.observers = observers
        self.solution_storage = solution_storage
        return

    @property
    def product(self):
        """
        A built ExhaustiveSearch
        """
        if self._product is None:
            constants = ExhaustiveSearchConstants
            dtype = self.configuration.get(section=self.section_header,
                                           option=constants.datatype_option,
                                           optional=False)
            minima = numpy.array(self.configuration.get_list(section=self.section_header,
                                                             option=constants.minima_option),
                                                             dtype=dtype)
            maxima = numpy.array(self.configuration.get_list(section=self.section_header,
                                                             option=constants.maxima_option),
                                                             dtype=dtype)
            increments = self.configuration.get_list(section=self.section_header,
                                                     option=constants.increments_option)
            if len(increments) == 1 and len(increments) < len(minima):
                increments = len(minima) * increments
            increments = numpy.array(increments, dtype)

            self._product = ExhaustiveSearch(minima=minima,
                                             maxima=maxima,
                                             increments=increments,
                                             quality=self.quality,
                                             observers=self.observers,
                                             solutions=self.solution_storage)
        return self._product
# end ExhaustiveSearchBuilder    
