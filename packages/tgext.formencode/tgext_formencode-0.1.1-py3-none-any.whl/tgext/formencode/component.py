# -*- coding: utf-8 -*-
import operator
from formencode import Schema
from formencode.api import Invalid
import tg
from tg.configurator.base import (ConfigurationComponent,
                                  ConfigReadyConfigurationAction)
from .i18n import set_formencode_translation, formencode_gettext


strip_string = operator.methodcaller('strip')


class FormencodeConfigurationComponent(ConfigurationComponent):
    """Support for Formencode validation"""
    id = 'formencode'

    def get_actions(self):
        return (
            ConfigReadyConfigurationAction(self._setup_i18n),
            ConfigReadyConfigurationAction(self._setup_validation),
        )

    def _setup_i18n(self, conf, app):
        tg.hooks.register("set_request_lang", _set_request_lang)

    def _setup_validation(self, conf, app):
        validation_validators = conf['validation.validators']
        if Schema not in validation_validators:
            validation_validators[Schema] = _validate_schema

        validation_exceptions = conf['validation.exceptions']
        if Invalid not in validation_exceptions:
            validation_exceptions.append(Invalid)

        validation_explode = conf['validation.explode']
        if Invalid not in validation_explode:
            validation_explode[Invalid] = _validation_explode


def _set_request_lang(languages):
    # Retrieve TG local context explicitly; hooks don't pass it.
    tgl = tg.request_local.context
    # Ensure languages is a sequence for gettext
    if isinstance(languages, (str, bytes)):
        languages = [languages]
    set_formencode_translation(languages, tgl)


def _validate_schema(schema, params):
    # An object used by FormEncode to get translator function
    formencode_state = type('state', (), {'_': staticmethod(formencode_gettext)})
    # A FormEncode Schema object - to_python converts the incoming
    # parameters to sanitized Python values
    return schema.to_python(params, formencode_state)


def _validation_explode(exception):
    errors = {}

    # Most Invalid objects come back with a list of errors in the format:
    # "fieldname1: error\nfieldname2: error"
    error_list = exception.__str__().split('\n')
    for error in error_list:
        field_value = list(map(strip_string, error.split(':', 1)))

        #if the error has no field associated with it,
        #return the error as a global form error
        if len(field_value) == 1:
            errors['_the_form'] = field_value[0]
            continue

        errors[field_value[0]] = field_value[1]

    return {"errors": errors, "values": getattr(exception, 'value', {})}
