
# third-party
import numpy

# this package
from tuna import BaseClass


class UniformConvolution(object):
    """
    A bounded uniform convolver
    """
    def __init__(self, half_range, lower_bound, upper_bound):
        """
        UniformConvolution constructor

        :param:

         - `half_range`: (-half_range, half_range) bounds the noise
         - `lower_bound`: minimum value to allow in convolved arrays
         - `upper_bound`: maximum value to allow in convolved array
        """
        self.half_range = half_range
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        return

    def __call__(self, vector):
        """
        adds random noise, bounded by the lower and upper bound values
        """
        tweak = numpy.random.uniform(low=-self.half_range,
                                     high=self.half_range,
                                     size=len(vector))
        tweaked = vector + tweak
        return tweaked.clip(self.lower_bound, self.upper_bound)
# end UniformConvolution    


class GaussianConvolution(BaseClass):
    """
    A Tweak that uses the Normal distribution
    """
    def __init__(self, lower_bound, upper_bound,
                 location=0, scale=1, number_type=float,
                 scalar_multiplier=1):
        """
        GaussianConvolution constructor

        :param:

         - `lower_bound`: minimum value to allow in tweaked arrays
         - `upper_bound`: maximum value to allow in tweaked arrays
         - `location`: Center of the distribution
         - `scale`: Spread of the distribution
         - `number_type`: type to cast random vector to
         - `scalar_multiplier`: value to multiply tweak by
        """
        super(GaussianConvolution, self).__init__()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.location = location
        self.scale = scale
        self.number_type = number_type
        self.scalar_multiplier = scalar_multiplier
        return

    def set_seed(self, seed):
        """
        Sets the numpy random seed (for reproducibility)
        """
        numpy.random.seed(seed)
        return

    def __call__(self, vector):
        """
        Adds normally distributed random noise to the vector

        Casts the tweak values to type specified by self.number_type

        :return: vector + noise, bounded by upper and lower bounds
        """
        tweak = numpy.random.normal(loc=self.location,
                                    scale=self.scale,
                                    size=len(vector)).astype(self.number_type)
        tweaked = vector + self.scalar_multiplier * tweak
        tweaked = tweaked.clip(self.lower_bound, self.upper_bound)
        self.logger.debug("Tweaked: {0}".format(tweaked))
        return tweaked
# class GaussianConvolution        


class GaussianConvolutionConstants(object):
    __slots__ = ()
    # options
    lower_bound = 'lower_bound'
    upper_bound = 'upper_bound'
    location = 'location'
    scale = 'scale'
    number_type = 'number_type'

    # defaults
    location_default = 0
    scale_default = 1
    number_type_default='float'     


class GaussianConvolutionBuilder(BaseClass):
    """
    builds GaussianConvolutions
    """
    def __init__(self, configuration, section):
        """
        GaussianConvolutionBuilder constructor

        :param:

         - `configuration`: configuration map
         - `section`: name of section with needed options
        """
        self.configuration = configuration
        self.section = section
        self._product = None
        return

    @property
    def product(self):
        """
        A built GaussianConvolution
        """
        if self._product is None:
            config = self.configuration
            constants = GaussianConvolutionConstants
            num_type = config.get(section=self.section,
                                  option=constants.number_type,
                                  optional=False)
            if num_type.lower().startswith('int'):
                number_type = int
            else:
                number_type = float
            location=config.get_float(section=self.section,
                                      option=constants.location,
                                      optional=True,
                                      default=constants.location_default)
            scale=config.get_float(section=self.section,
                                   option=constants.scale,
                                   optional=True,
                                   default=constants.scale_default)
            lower_bound=config.get_float(section=self.section,
                                         option=constants.lower_bound)
            upper_bound=config.get_float(section=self.section,
                                         option=constants.upper_bound)

            self._product = GaussianConvolution(location=location,
                                                scale=scale,
                                                lower_bound=lower_bound,
                                                upper_bound=upper_bound,
                                                number_type=number_type)
                                                                             
                                                                             
        return self._product        


class XYConvolution(BaseClass):
    """
    A Tweak that uses the Normal distribution
    """
    def __init__(self, x_min, x_max, y_min, y_max,
                 location=0, scale=1, number_type=float,
                 scalar_multiplier=1):
        """
        GaussianConvolution constructor

        :param:

         - `x_min`: minimum value for x-value
         - `x_max`: maximum value for x-value
         - `y_min`: minimum value for y-value
         - `y_max`: maximum value for y-value
         - `location`: Center of the distribution
         - `scale`: Spread of the distribution
         - `number_type`: type to cast random vector to
         - `scalar_multiplier`: value to multiply tweak by
        """
        super(XYConvolution, self).__init__()
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.location = location
        self.scale = scale
        self.number_type = number_type
        self.scalar_multiplier = scalar_multiplier
        return

    def set_seed(self, seed):
        """
        Sets the numpy random seed (for reproducibility)
        """
        numpy.random.seed(seed)
        return

    def __call__(self, vector):
        """
        Adds normally distributed random noise to the vector

        Casts the tweak values to type specified by self.number_type

        :return: vector + noise, bounded by upper and lower bounds
        """
        x = self.number_type(numpy.random.normal(loc=self.location,
                                                 scale=self.scale))
        y = self.number_type(numpy.random.normal(loc=self.location,
                                                 scale=self.scale))

        x = max(self.x_min, x)
        x = min(self.x_max, x)
        y = max(self.y_min, y)
        y = max(self.y_max, y)
        tweaked = vector + self.scalar_multiplier * numpy.array([x, y])
        self.logger.debug("Tweaked: {0}".format(tweaked))
        return tweaked.clip(self.lower_bound, self.upper_bound)
# class XYConvolution


class XYConvolutionConstants(object):
    __slots__ = ()
    # options
    x_min = 'xmin'
    x_max = 'xmax'
    y_min = 'ymin'
    y_max = 'ymax'
    location = 'location'
    scale = 'scale'
    number_type = 'number_type'

    # defaults
    location_default = 0
    scale_default = 1
    number_type_default='float'     


class XYConvolutionBuilder(BaseClass):
    """
    builds XYConvolutions
    """
    def __init__(self, configuration, section):
        """
        XYConvolutionBuilder constructor

        :param:

         - `configuration`: configuration map
         - `section`: name of section with needed options
        """
        self.configuration = configuration
        self.section = section
        self._product = None
        return

    @property
    def product(self):
        """
        A built XYConvolution
        """
        if self._product is None:
            config = self.configuration
            constants = XYConvolutionConstants
            num_type = config.get(section=self.section,
                                  option=constants.number_type,
                                  optional=False)
            if num_type.lower().startswith('int'):
                number_type = int
            else:
                number_type = float
            location=config.get_float(section=self.section,
                                      option=constants.location,
                                      optional=True,
                                      default=constants.location_default)
            scale=config.get_float(section=self.section,
                                   option=constants.scale,
                                   optional=True,
                                   default=constants.scale_default)
            x_min=config.get_float(section=self.section,
                                         option=constants.x_min)
            x_max=config.get_float(section=self.section,
                                         option=constants.x_max)
            
            y_min=config.get_float(section=self.section,
                                         option=constants.y_min)
            y_max=config.get_float(section=self.section,
                                         option=constants.y_max)

            self._product = XYConvolution(location=location,
                                                scale=scale,
                                                x_min=x_min,
                                                x_max=x_max,
                                                y_min=y_min,
                                                y_max=y_max,
                                                number_type=number_type)
        return self._product        


if __name__ == '__builtin__':
    gaussian = GaussianConvolution(lower_bound=-100,
                                   upper_bound=100)
    candidate = numpy.array([5,6])
    print gaussian(candidate)
    
    # change the candidate, move the mean up, widen the distribution
    gaussian.scale = 20
    gaussian.location = 5
    candidate = numpy.array([0, 1, 2])
    gaussian.number_type = int
    print gaussian(candidate)
    
    # clip the values so it's right-skewed
    gaussian.lower_bound = 5
    gaussian.upper_bound = 100
    print gaussian(candidate)
