
# python standard library
import random

# third party
from behave import given, when, then
from mock import call, MagicMock
from hamcrest import assert_that, equal_to

# this package
from tuna.components.composite import SimpleComposite


@given("a SimpleComposite of components is ready")
def build_composite(context):
    context.args = dict(zip('a b c'.split(), (1,2,3)))
    context.logger = MagicMock(name='logger')
    components = [MagicMock(name='component_{0}'.format(component))
                  for component in xrange(random.randrange(20))]
    context.composite = SimpleComposite(components=components)
    context.composite._logger = context.logger
    return

@when("the SimpleComposite is called")
def call_composite(context):
    context.composite(**context.args)
    return

@then("it will log the arguments and components called")
def check_logging(context):
    expected = ([call("SimpleComposite arguments: {0}".format(context.args))] +
                [call("SimpleComposite calling '{0}'".format(component))
                 for component in context.composite.components])
    assert_that(context.logger.debug.mock_calls, equal_to(expected))
    return
