
# python standard library
from abc import ABCMeta, abstractmethod, abstractproperty
import os

# this package 
from tuna import BaseClass, ConfigurationError
from tuna.infrastructure.helppage import HelpPage



in_pweave = __name__ == '__builtin__'


class BasePlugin(BaseClass):
    """
    An abstract base-class for plugins

    :param:

     - `configuration`: configuration-map for plugin configuration
    """
    __metaclass__ = ABCMeta
    def __init__(self, configuration=None, section_header=None):
        """
        BasePlugin constructor

        :param:

         - `configuration`: a ConfigurationMap for the product
         - `section_header`: header in the configuration for this plugin's info
        """
        super(BasePlugin, self).__init__()
        self._logger = None
        self._help = None
        self._config = None
        self._product = None
        self._help_page = None        
        self._sections = None
        self._configuration = configuration
        self._section_header = section_header
        return

    @property
    def section_header(self):
        """
        The section in the configuration file

        :raise: ConfigurationError if not set
        """
        if self._section_header is None:
            raise ConfigurationError("'{0}' needs `section_header` for configuration".format(self.__class__.__name__))
        return self._section_header

    @property
    def configuration(self):
        """
        A configuration map to get settings from

        :raise: ConfigurationError if not set
        """
        if self._configuration is None:
            raise ConfigurationError("{0} needs a ConfigurationMap".format(self.__class__.__name__))
        return self._configuration

    @abstractproperty
    def sections(self):
        """
        A (ordered) dictionary for the help page
        """
        return self._sections

    @property
    def help_page(self):
        """
        A HelpPage to use if self.sections has been defined
        """
        if self._help_page is None and self.sections is not None:
            self._help_page = HelpPage(sections=self.sections)
        return self._help_page                        

    def help(self, width=80):
        """
        Prints a help-string for the plugin

        :param:

         - `width`: number of characters wide to print help
        """
        if self.sections is None:
            print "'{0}' offers you no help. Such is life.".format(self.__class__.__name__)
        else:
            self.help_page.wrap = width
            self.help_page()
        return

    @abstractproperty
    def product(self):
        """
        Abstract Property: The plugin (Component implementation)
        """
        return

    @abstractmethod
    def fetch_config(self):
        """
        Abstract Method: Get sample config-file snippet required by this plugin
        """
        return   
# end class BasePlugin                
