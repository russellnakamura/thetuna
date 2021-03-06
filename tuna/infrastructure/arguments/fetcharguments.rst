The Fetch Sub-Command Arguments
===============================
::

    """fetch subcommand
        
    usage: tuna fetch -h
           tuna fetch [<name>...]  [--module <module> ...] [-c]
    
    positional arguments:
        <name>                         List of plugin-names (default=['Optimize
    r'])
    
    optional arguments:
        -h, --help                     Show this help message and exit
        -c, --components               If set, looks for `components` instead o
    f `plugins`
        -m, --module <module> ...      Non-optimizer modules
    """
    
    



These are arguments for the `fetch` sub-command (see the :ref:`developer documentation <docopt-reproducingoptimizer-fetch-sub-command>` for more information).



.. _optimizer-interface-arguments-fetch-constants:

The Fetch Arguments Constants
-----------------------------

::

    class FetchArgumentsConstants(object):
        """
        Constants for the `fetch` sub-command arguments
        """    
        __slots__ = ()
        # arguments and options
        names = "<name>"
        modules = '--module'
        components = '--components'
        
        # defaults
        default_names = ['Tuna']
    
    



.. _optimizer-interface-arguments-fetch-arguments:

The FetchArguments
------------------

.. uml::

   BaseArguments <|-- FetchArguments


.. module:: tuna.infrastructure.arguments.fetcharguments

.. autosummary::
   :toctree: api

   Fetch
   Fetch.names
   Fetch.modules
   Fetch.components
   Fetch.reset



.. _optimizer-interface-arguments-fetch-strategy:

The FetchStrategy
-----------------

.. autosummary::
   :toctree: api

   FetchStrategy
   FetchStrategy.function



The `function` method is wrapped by the :ref:`try_except decorator <optimizer-commoncode-try-except-decorator>` so it should never crash.
