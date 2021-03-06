Example Functions
=================

These use real-valued functions that map a vector input to an output.



Sphere
------

This is taken from [EOM]_. It creates a sphere. If the domain is narrow enough it will create 4 maxima. Although my original intention was to allow any number of dimensions, it's getting too hard so I'm going to limit the inputs to two-dimensions until I understand numpy better.

.. currentmodule:: optimization.datamapping.examples.functions
.. autosummary::
   :toctree: api

   SphereMapping
   SphereMapping.mapping
   SphereMapping.x
   SphereMapping.y
   SphereMapping.z
   SphereMapping.reset

::

    class SphereMapping(object):
        """
        Creates a Quality Mapping with spherical data
        """
        def __init__(self, start=-5.12, stop=5.12, steps=1000):
            """
            Sphere Mapping
    
            :param:
    
             - `start`: low-value for x and y
             - `stop`: high-value for x and y
             - `steps`: size of x and y
            """
            self._mapping = None
            self.start = start
            self.stop = stop
            self.steps = steps
            self._x = None
            self._y = None
            self._z = None
            return
    
        @property
        def x(self):
            """
            x-axis data
            """
            if self._x is None:
                self._x = numpy.linspace(self.start,
                                   self.stop,
                                   self.steps)
            return self._x
    
        @property
        def y(self):
            """
            2-d array (meshgrid for y-axis)
            """
            if self._y is None:
                self._y = numpy.linspace(self.start,
                                   self.stop,
                                   self.steps)
            return self._y
    
        @property
        def z(self):
            """
            2-d array (meshgrid for z-axis)
            """
            if self._z is None:
                if len(self.x.shape) == 1:
                    # apply meshgrid
                    self._x, self._y = numpy.meshgrid(self.x, self.y)
                self._z = self.x**2 + self.y**2
            return self._z
    
        @property
        def mapping(self):
            """
            Built QualityMapping
            """
            if self._mapping is None:
                mapping_function = lambda argument: numpy.sum(argument**2)
                self._mapping = QualityMapping(ideal=self.z.max(),
                                               mapping=mapping_function)
            return self._mapping
    
        def reset(self):
            """
            Resets the mapping function
            """
            self.mapping.reset()
            return
    # end SphereMapping
    



The SphereMapping maintains the x, y, and z arrays so that they can be plotted. They have been transformed using numpy's `meshgrid` so they are each 2-d.

.. '

The Rastrigin
-------------

.. autosummary::
   :toctree: api

   RastriginMapping
   RastriginMapping.x
   RastriginMapping.y
   RastriginMapping.z
   RastriginMapping.mapping
   RastriginMapping.reset

::

    two_pi = 2 * numpy.pi
    def rastrigin(argument):
        return 10*len(argument) + numpy.sum(argument**2 - 10
                                            * numpy.cos(two_pi * argument))
    
    

::

    class RastriginMapping(object):
        """
        Creates a Quality Mapping with the Rastrigin function
        """
        def __init__(self, start=-5.12, stop=5.12, steps=1000):
            """
            Rastrigin Mapping Constructor
    
            :param:
    
             - `start`: low-value for x and y
             - `stop`: high-value for x and y
             - `steps`: size of x and y
            """
            self._mapping = None
            self.start = start
            self.stop = stop
            self.steps = steps
            self._x = None
            self._y = None
            self._z = None
            self.meshed = False
            return
    
        @property
        def x(self):
            """
            x-axis data
            """
            if self._x is None:
                self._x = numpy.linspace(self.start,
                                   self.stop,
                                   self.steps)
            return self._x
    
        @property
        def y(self):
            """
            2-d array (meshgrid for y-axis)
            """
            if self._y is None:
                self._y = numpy.linspace(self.start,
                                   self.stop,
                                   self.steps)
            return self._y
    
        @property
        def z(self):
            """
            2-d array (meshgrid for z-axis)
            """
            if self._z is None:
                # apply meshgrid
                if not self.meshed:
                    self.meshed = True
                    # this doesn't work for plotting
                    self._x, self._y = numpy.meshgrid(self.x, self.y)
                    self._z = (20 + (self.x**2-10 * numpy.cos(two_pi*self.x)) +
                               (self.y**2-10 * numpy.cos(two_pi*self.y)))
            return self._z
    
        @property
        def mapping(self):
            """
            Built QualityMapping
            """
            if self._mapping is None:
                self._mapping = QualityMapping(ideal=self.z.max(),
                                               mapping=rastrigin)
            return self._mapping
    
        def reset(self):
            """
            Resetes the mapping
            """
            self.mapping.reset()
            return
    # end RastriginMapping
    

