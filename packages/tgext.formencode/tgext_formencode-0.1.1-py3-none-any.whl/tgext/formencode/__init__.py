from .decorators import variable_decode


def plugme(configurator, options=None):
    from .component import FormencodeConfigurationComponent
    configurator.register(FormencodeConfigurationComponent, after="validation")
    return dict(appid='tgext.formencode')

