
# python standard library
from contextlib import nested
import random
from StringIO import StringIO

# third party
from behave import given, when, then
from mock import MagicMock, mock_open, patch, call
from hamcrest import assert_that, equal_to, instance_of

# this package
from tuna.commands.dump import TheDump
from tuna import BaseComponent


@given("a TheDump object is created")
def dump_creation(context):
    context.command = "aoeu"
    context.connection = MagicMock()
    context.identifier = "dumpidentity"
    context.filename = 'dumpfilename'
    context.timeout = random.randrange(10)
    context.mode = random.choice('aw')
    context.dump = TheDump(command=context.command,
                           connection=context.connection,
                           identifier=context.identifier,
                           filename=context.filename,
                           timeout=context.timeout,
                           mode=context.mode)
    assert_that(context.dump, instance_of(BaseComponent))
    return

@when("TheDump object is called")
def dump_call(context):
    context.file = mock_open()
    context.output = StringIO("".join(('{0}\n'.format(letter) for letter in"a b c".split())))
    context.error = StringIO('')
    context.connection.exec_command.return_value = None, context.output, context.error
    context.datetime = MagicMock(name='datetime')
    context.timestamp = 'ummagumma'
    context.strftime = MagicMock(name='strftime')
    context.datetime.now.return_value = context.strftime

    context.strftime.strftime.return_value = context.timestamp
    with nested(patch('__builtin__.open', context.file),
                patch('datetime.datetime', context.datetime)):
        context.dump()
    print context.datetime.now()
    print context.strftime()
    return

@then("TheDump sends its command to its connection")
def check_command(context):
    context.connection.exec_command.assert_called_with(context.command,
                                                       timeout=context.timeout)
    return

@then("TheDump redirects the command output to storage")
def check_storage(context):
    context.file.assert_called_with(context.filename, context.mode)
    expected = [call('{1},{0}\n'.format(letter
                                        , context.timestamp))
                                        for letter in 'a b c'.split()]
    handle = context.file()
    assert_that(handle.write.mock_calls, equal_to(expected))
    return
