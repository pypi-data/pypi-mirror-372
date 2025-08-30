import gettext as _gettext
from gettext import NullTranslations
import formencode
import tg
from tg.i18n import LanguageError, ugettext


_localdir = formencode.api.get_localedir()


def formencode_gettext(value):
    trans = ugettext(value)
    # Translation failed, try formencode
    if trans == value:
        try:
            fetrans = tg.translator._formencode_translation
        except (AttributeError, TypeError):
            # the translator was not set in the TG context
            # we are certainly in the test framework
            # let's make sure won't return something that is ok with the caller
            fetrans = None

        if not fetrans:
            fetrans = NullTranslations()

        translator_gettext = getattr(fetrans, 'ugettext', fetrans.gettext)
        trans = translator_gettext(value)

    return trans



def set_formencode_translation(languages, tgl):
    """Set request specific translation of FormEncode."""
    try:
        formencode_translation = _gettext.translation('FormEncode',
                                                      languages=languages,
                                                      localedir=_localdir)
    except IOError as error:
        raise LanguageError('IOError: %s' % error)
    tgl.translator._formencode_translation = formencode_translation
