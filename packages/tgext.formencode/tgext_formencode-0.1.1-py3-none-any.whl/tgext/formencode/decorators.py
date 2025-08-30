from formencode import variabledecode as _variabledecode
from tg.decorators import before_validate


@before_validate
def variable_decode(remainder, params):
    """Best-effort formencode.variabledecode on the params before validation.

    If any exceptions are raised due to invalid parameter names, they are
    silently ignored, hopefully to be caught by the actual validator.
    Note that this decorator will *add* parameters to the method, not remove.
    So for instance a method will move from {'foo-1':'1', 'foo-2':'2'}
    to {'foo-1':'1', 'foo-2':'2', 'foo':['1', '2']}.

    """
    try:
        new_params = _variabledecode.variable_decode(params)
        params.update(new_params)
    except:
        pass
