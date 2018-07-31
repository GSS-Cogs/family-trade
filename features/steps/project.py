@given(u'the "{dataset}" dataset is published in PMD')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the "ONS ABS" dataset is published in PMD')

@when(u'I lock dimension "{dimension}" to "{value}"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I lock dimension "employment" to "employment-size-bands/any"')

@when(u'I lock the measure type to "{measure}"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I lock the measure type to "count"')

@when(u'I lock the reference period to "{period}"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I lock the reference period to "year/2016"')

@when(u'download the resulting table')
def step_impl(context):
    raise NotImplementedError(u'STEP: When download the resulting table')


@then(u'the table should look like')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the table should look like')
