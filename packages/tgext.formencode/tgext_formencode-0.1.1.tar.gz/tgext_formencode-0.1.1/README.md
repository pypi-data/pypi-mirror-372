# tgext.formencode
Support Formencode Schema validation in TurboGears 2.5+

## Usage

```
    import tgext.formencode

    cfg = FullStackApplicationConfigurator()
    tgext.formencode.plugme(cfg)
    cfg.make_wsgi_app({}, {})
```

## Variables Decoding

Adds support for decoding lists and dictionaries passed to
turbogears controllers in the variableencoded format:
``{"l": [1, 2]} -> {"l-0": 1, "l-1": 2}``

```
    from tgext.formencode import variable_decode

    class MyController(TGController):
        @variable_decode
        def test_vardec(self, **kw):
            print(kw)
            return ""
```
