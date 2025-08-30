from unittest import mock

import tg
from tg.util.webtest import test_context

from tgext.formencode import i18n


def test_formencode_gettext_nulltranslation():
    def nop_gettext(v):
        # This makes _formencode_gettext fallback to
        # the actual formencode translator instead of tg one.
        return v

    with mock.patch.object(i18n, 'ugettext', new=nop_gettext):
        assert i18n.formencode_gettext('something') == 'something'


def test_formencode_gettext():
    _formencode_translation = mock.Mock(ugettext=lambda v: "TRANSLATED")

    with test_context(app=None):
        with mock.patch.object(tg.translator, '_formencode_translation', create=True,
                               new=_formencode_translation):
            assert i18n.formencode_gettext('something') == 'TRANSLATED'
