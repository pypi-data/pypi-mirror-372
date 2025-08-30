from webtest import TestApp
from tg import TGController, expose, FullStackApplicationConfigurator
from tgext.formencode import variable_decode, plugme


class RootController(TGController):
    @expose('json')
    @variable_decode
    def test_vardec(self, **kw):
        return kw


class TestDecorators:
    def setup_method(self):
        configurator = FullStackApplicationConfigurator()
        configurator.update_blueprint({
            'root_controller': RootController()
        })
        plugme(configurator)
        self.app = TestApp(configurator.make_wsgi_app())

    def test_variable_decode(self):
        from formencode.variabledecode import variable_encode
        obj = dict(a=['1','2','3'], b=dict(c=[dict(d='1')]))
        params = variable_encode(dict(obj=obj), add_repetitions=False)
        resp = self.app.get('/test_vardec', params=params)
        assert resp.json['obj'] == obj, (resp.json['obj'], obj)

    def test_variabledecode_fail(self):
        resp = self.app.get('/test_vardec', params={'test-1': '1',
                                                    'test-2': 2,
                                                    'test--repetitions': 'hi'})
        assert resp.json['test-1'] == '1', resp.json
        assert resp.json['test--repetitions'] == 'hi', resp.json
        assert 'test' not in resp.json, resp.json

    def test_variabledecode_partial_fail(self):
        resp = self.app.get('/test_vardec', params={'test-1': '1',
                                                    'test-2': 2,
                                                    'test-': 4})
        assert resp.json['test-1'] == '1'
        assert resp.json['test-'] == '4'
        assert len(resp.json['test']) == 2
