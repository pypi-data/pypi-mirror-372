from webtest import TestApp
import tg
from tg import TGController, expose, validate, FullStackApplicationConfigurator
from tg.controllers.util import validation_errors_response

from formencode import validators, Schema

from tgext.formencode import plugme


class Pwd(Schema):
    pwd1 = validators.String(not_empty=True)
    pwd2 = validators.String(not_empty=True)
    chained_validators = [validators.FieldsMatch('pwd1', 'pwd2')]


class ColonValidator(validators.FancyValidator):
    def _validate_python(self, value, state):
        raise validators.Invalid('ERROR: Description', value, state)


class RootController(TGController):
    @expose()
    @validate({'param': validators.Int()},
              error_handler=validation_errors_response)
    def formencode_dict_validation(self, **kwargs):
        return 'NO_ERROR'

    @expose()
    @validate(validators=Pwd())
    def password(self, pwd1, pwd2):
        if tg.request.validation.errors:
            return "There was an error"
        else:
            return "Password ok!"

    @expose('json:')
    @validate(validators={"e": ColonValidator()})
    def error_with_colon(self, e):
        errors = tg.request.validation.errors
        return dict(errors=str(errors))


class TestFormencodeValidation:
    def setup_method(self):
        configurator = FullStackApplicationConfigurator()
        configurator.update_blueprint({
            'root_controller': RootController()
        })
        plugme(configurator)
        self.app = TestApp(configurator.make_wsgi_app())

    def test_schema_validation_error(self):
        """Test schema validation"""
        form_values = {'pwd1': 'me', 'pwd2': 'you'}
        resp = self.app.post('/password', form_values)
        assert "There was an error" in resp, resp
        form_values = {'pwd1': 'you', 'pwd2': 'you'}
        resp = self.app.post('/password', form_values)
        assert "Password ok!" in resp, resp

    def test_formencode_dict_validation(self):
        resp = self.app.post('/formencode_dict_validation', {'param': "7"})
        assert 'NO_ERROR' in str(resp.body), resp

        resp = self.app.post('/formencode_dict_validation', {'param': "hello"}, status=412)
        assert 'Please enter an integer value' in str(resp.body), resp

    def test_error_with_colon(self):
        resp = self.app.post('/error_with_colon', {'e':"fakeparam"})
        assert 'Description' in str(resp.body), resp.body

