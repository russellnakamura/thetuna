
# python standard library
import sys

# this package
from tuna.infrastructure.ryemother import RyeMother
from tuna import BaseClass
from tuna.infrastructure.arguments import BaseArguments


class ArgumentBuilder(BaseClass):
    """
    An adapter so this can go where the ArgumentClinic was
    """
    def __init__(self, args=None):
        """
        ArgumentBuilder Constructor

        :param:

         - `args`: list of args to use instead of sys.argv
        """
        super(ArgumentBuilder, self).__init__()
        self.args = args
        self._rye_mother = None
        self._argument_definitions = None
        return

    @property
    def rye_mother(self):
        """
        A gatherer of children
        """
        if self._rye_mother is None:
            self._rye_mother = RyeMother(group='tuna.subcommands',
                                         name='subcommands',
                                         keyfunction=lambda k: getattr(k, 'lower')())
        return self._rye_mother

    @property
    def argument_definitions(self):
        """
        A dict of name:class definition for BaseArgument children
        """
        if self._argument_definitions is None:
            self._argument_definitions = self.rye_mother(BaseArguments)
        return self._argument_definitions

    def __call__(self):
        """
        Fake parse-args

        :return: sub-argument (e.g. RunArguments) based on command in args
        """
        args = BaseArguments(args=self.args)
        try:
            return self.argument_definitions[args.command](args=self.args)
        except KeyError as error:
            self.logger.debug(error)
            self.logger.error("Unknown sub-command '{0}'".format(args.command))
            print args.usage
            sys.exit()
        return args
