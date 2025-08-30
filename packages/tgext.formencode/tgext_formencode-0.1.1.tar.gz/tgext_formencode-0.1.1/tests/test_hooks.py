import pytest
import gettext

import tg
from tg import TGController
from tg import FullStackApplicationConfigurator
from tg.util.webtest import test_context
import tgext.formencode


class RootController(TGController):
    pass


def test_set_request_lang_sets_formencode_translation():
    """Hook should set a FormEncode translation for the request.

    TurboGears hooks don't pass request locals; the handler must
    retrieve them from tg.request_local.context. After firing the
    hook, ensure translation is not NullTranslations and language
    metadata corresponds to requested locale.
    """
    configurator = FullStackApplicationConfigurator()
    configurator.update_blueprint({
        'root_controller': RootController()
    })
    tgext.formencode.plugme(configurator)
    configurator.make_wsgi_app()

    with test_context(app=None):
        tg.hooks.notify('set_request_lang', ['pt_BR'])

        # Access the request-local TG context explicitly
        tgl = tg.request_local.context
        trans = getattr(tgl.translator, '_formencode_translation', None)

        assert trans is not None, "FormEncode translation not set on translator"
        assert isinstance(trans, gettext.GNUTranslations), (
            f"Expected GNUTranslations, got {type(trans)}"
        )

        # Compare with a known pt_BR GNUTranslations instance by catalog
        from tgext.formencode import i18n as fe_i18n
        expected = gettext.translation('FormEncode', languages=['pt_BR'], localedir=fe_i18n._localdir)
        assert isinstance(expected, gettext.GNUTranslations)
        assert trans._catalog == expected._catalog
