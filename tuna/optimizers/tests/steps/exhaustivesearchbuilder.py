
# third-party
from behave import given, when, then
from mock import MagicMock
from hamcrest import assert_that, is_, equal_to, instance_of
import numpy

# this package
from tuna.optimizers.exhaustivesearch import ExhaustiveSearchConstants
from tuna.optimizers.exhaustivesearch import ExhaustiveSearchBuilder
from tuna.optimizers.exhaustivesearch import ExhaustiveSearch


@given("a configuration with ExhaustiveSearch options")
def setup_configuration(context):
    context.configuration = MagicMock()
    context.observers = MagicMock()
    context.kwargs = {}
    context.kwargs[ExhaustiveSearchConstants.minima_option] = range(4)
    context.kwargs[ExhaustiveSearchConstants.maxima_option] = range(4)
    context.kwargs[ExhaustiveSearchConstants.increments_option] = range(4)
    context.kwargs[ExhaustiveSearchConstants.datatype_option] = 'int'
    context.quality = MagicMock()
    context.solution_storage = MagicMock()
    def get(**kwargs):
        return context.kwargs[kwargs['option']]

    context.configuration.get_list.side_effect = get
    context.configuration.get.side_effect = get

@when("the ExhaustiveSearchBuilder product is retrieved")
def build_product(context):
    context.section_header = 'gridsearch'
    context.builder = ExhaustiveSearchBuilder(configuration=context.configuration,
                                              section_header=context.section_header,
                                              quality=context.quality,
                                              observers=context.observers,
                                              solution_storage=context.solution_storage)
    return

@then("the ExhaustiveSearchBuilder product is an ExhaustiveSearch")
def check_product(context):
    assert_that(context.configuration, is_(context.builder.configuration))
    assert_that(context.section_header, equal_to(context.builder.section_header))
    assert_that(context.builder.product, instance_of(ExhaustiveSearch))
    return


@given("a configuration with one increment and multiple minima and maxima")
def setup_configuration(context):
    context.kwargs[ExhaustiveSearchConstants.increments_option] = [1]
    return

@then("the ExhaustiveSearch has an increment of the same size as the minima and maxima")
def check_increment(context):
    expected = numpy.ones(4)
    assert_that(numpy.array_equal(context.builder.product.increments,
                                  expected))
    return


@given("a configuration with minima and maxima of different sizes")
def mismatched_minima_maxima(context):
    context.kwargs[ExhaustiveSearchConstants.minima_option] = range(6)
    context.kwargs[ExhaustiveSearchConstants.maxima_option] = range(4)
    return

@then("a ConfigurationError is raised")
def check_error(context):
    return
