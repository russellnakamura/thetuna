
# python standard library
import inspect

# this package
from tuna import MODULES_SECTION
from tuna.infrastructure.quartermaster import QuarterMaster
from component import BaseComponent
from tuna.infrastructure.crash_handler import try_except
from tuna import RESET
from tuna import BOLD
from tuna.parts.countdown.countdown import TimeTracker
from tuna import BaseClass, TunaError


class Composite(BaseComponent):
    """
    A Composite to hold and execute Components
    """
    def __init__(self, components=None,
                 error=None, error_message=None,
                 identifier=None,
                 component_category=None,
                 time_remains=None):
        """
        Composite Constructor

        :param:

         - `components`: list of components
         - `error`: Exception to catch when calling components
         - `error_message`: string for header of error messages
         - `component_category`: label for error messages when reporting component actions
         - `identifier`: something to identify this when it starts the call
         - ``time_remains`` - a TimeTracker or CountdownTimer
        """
        super(Composite, self).__init__()
        self.error = error
        self.error_message = error_message
        self.identifier = identifier
        self.component_category = component_category
        self._logger = None
        self._components = components
        self._time_remains = time_remains
        return

    @property
    def components(self):
        """
        The list of components
        """
        if self._components is None:
            self._components = []
        return self._components

    @property
    def time_remains(self):
        """
        :return: TimeTracker (default) or CountdownTimer object
        """
        if self._time_remains is None:
            self._time_remains = TimeTracker()
        return self._time_remains

    @time_remains.setter
    def time_remains(self, countdown):
        """
        Sets the time_remains attribute

        :param:

         - ``countdown``: a CountdownTimer to call
        """
        self._time_remains = countdown
        return

    def add(self, component):
        """
        appends the component to self.components

        :param:

         - `component`: A Component

        :postcondition: component appended to components
        """
        self.components.append(component)
        return

    def remove(self, component):
        """
        Removes the component from the components (if it was there)
        """
        try:
            self.components.remove(component)
        except ValueError as error:
            self.logger.debug(error)
        return

    def __iter__(self):
        """
        Iterates over the components
        """
        for component in self.components:
            yield component

    def __len__(self):
        """
        Counts the components

        :return: count of components
        """
        return len(self.components)

    def __getitem__(self, index):
        """
        gets slice or index of components
        """
        return self.components[index]

    @try_except
    def one_call(self, component):
        """
        Calls the  component (pulled out into a method to catch the exceptions)

        :raise:

         - `TunaError` if component is not callable
        """
        if not hasattr(component, '__call__'):
            raise TunaError(("'{0}' has not implemented the __call__ interface. " 
                            "What a way to run a railroad.").format(component.__class__.__name__))
        component()
        return

    def __call__(self):
        """
        The main interface -- starts components after doing a check_rep

        """
        self.logger.debug("{b}** Checking the Composite Class Representation **{r}".format(b=BOLD,
                                                                                          r=RESET))

        self.check_rep()
        count_string = "{b}** {l} {{c}} of {{t}} ('{{o}}') **{r}".format(b=BOLD, r=RESET,
                                                                         l=self.component_category)

        self.logger.info("{b}*** {c} Started ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.identifier))
        
        total_count = len(self.components)
        
        self.logger.info("{b}*** Starting {c} ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.component_category))

        # the use of time-remains is meant to facilitate repeated re-use of the same component calls
        while self.time_remains():
            for count, component in enumerate(self.components):
                self.logger.info(count_string.format(c=count+1,
                                                     t=total_count,
                                                     o=str(component)))                                                 
                self.one_call(component)
        self.logger.info("{b}*** {c} Ended ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.identifier))        
        return

    def check_rep(self):
        """
        Checks the representation invariant     

        :raise: ConfigurationError
        """
        try:
            # these checks only make sense when used in the infrastructure
            # at some point this should be generalized somehow so it can act like a
            # composite proper
            assert inspect.isclass(self.error),(
                "self.error must be an exception, not {0}".format(self.error))
            assert issubclass(self.error, Exception),(
                "self.error needs to be an exception, not {0}".format(self.error))
            assert self.error_message is not None, (
                "self.error_message must not be None")
            assert self.component_category is not None, (
                "self.component_category must not be None")

            # check all your children
            for component in self.components:
                if hasattr(component, 'check_rep'):
                    component.check_rep()
                else:
                    self.log_error(error="'{0}' hasn't implemented the 'check_rep' method.".format(component.__class__.__name__),
                                    message="Thanks for the sour persimmons, cousin.")

        except AssertionError as error:
            raise ConfigurationError(str(error))
        return

    def close(self):
        """
        calls the `close` method on each component (close should tear-down resources)

        :postcondition: comuponents closed and self.components is None
        """
        for component in self.components:
            if hasattr(component, 'close'):
                component.close()
            else:
                self.logger.warning("'{0}' hasn't implemented the 'close' method. We hate him.".format(component))
        self._components = None
        return

    def reset(self):
        """
        calls the `reset` method on each component (reset should prepare for repeat execution)

        :postcondition: comuponents closed and self.components is None
        """
        for component in self.components:
            if hasattr(component, 'reset'):
                component.reset()
            else:
                self.logger.warning("'{0}' hasn't implemented the 'reset' method. We hate him.".format(component))
        return

    def __str__(self):
        return ("{2} -- Traps: {0}, "
                "{3} Components: {1}").format(self.error.__name__,
                                         self.component_category,
                                         self.__class__.__name__,
                                         len(self.components))
        
#end class Composite


class SimpleComposite(BaseClass):
    """
    A simpler implementation of a composite.
    """
    def __init__(self, components=None):
        """
        SimpleComponent constructor

        :param:

         - `components`: optional list of components
        """        
        super(SimpleComposite, self).__init__()
        self._components = components
        return

    @property
    def components(self):
        """
        A list of callable objects
        """
        if self._components is None:
            self._components = []
        return self._components        

    def add(self, component):
        """
        appends the component to self.components
        """
        self.components.append(component)
        return

    def remove(self, component):
        """
        removes the component from components if it's there
        """
        if component in self.components:
            self.components.remove(component)
        return

    def __contains__(self, component):
        """
        To make membership checking easier, this checks if a component is in the components
        """
        return component in self.components

    def check_rep(self):
        """
        calls check-rep on the children
        """
        for component in self.components:
            component.check_rep()
        return

    def close(self):
        """
        Closes children
        """
        for component in self.components:
            component.close()
        return

    def __call__(self, **kwargs):
        """
        The main interface, calls all components, passing in kwargs
        """
        self.logger.debug("SimpleComposite arguments: {0}".format(kwargs))
        for component in self.components:
            self.logger.debug("SimpleComposite calling '{0}'".format(component))
            component(**kwargs)
        return

    def __iter__(self):
        """
        Traverses the components and yields them
        """
        for component in self.components:
            yield component
        return
# end class SimpleComposite    


class SimpleCompositeBuilder(object):
    """
    A builder of quality-composites
    """
    def __init__(self, configuration, section_header, option='components', name='components'):
        """
        SimpleCompositeBuilder constructor

        :param:

         - `configuration`: configuration map with options to build this thing
         - `section_header`: section in the configuration with values needed
         - `option`: option name in configuration section with list of components
         - `name`: name used in setup.py to identify location of components
        """
        self.configuration = configuration
        self.section_header = section_header
        self.name = name
        self.option = option
        self._product = None
        return

    @property
    def product(self):
        """
        A built Simple Composite
        """
        if self._product is None:
            quartermaster = QuarterMaster(name=self.name)
            self._product = SimpleComposite()
            defaults = self.configuration.defaults
            external_modules = [option for option in self.configuration.options(MODULES_SECTION)
                                 if option not in defaults]
            quartermaster.external_modules = external_modules
            for component_section in self.configuration.get_list(section=self.section_header,
                                                                 option=self.option):
                component_name = self.configuration.get(section=component_section,
                                                        option='component',
                                                        optional=False)
                component_def = quartermaster.get_plugin(component_name)
                component = component_def(self.configuration,
                                          component_section).product
                self._product.add(component)
            if not len(self._product.components):
                raise ConfigurationError("Unable to build components using 'components={0}'".format(self.section_header,
                                                                                                            option=self.option))
        return self._product
