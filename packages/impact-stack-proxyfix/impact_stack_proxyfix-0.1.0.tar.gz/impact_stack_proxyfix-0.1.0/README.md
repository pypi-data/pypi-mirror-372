# WSGI Proxyfix

This is a modified version of the ProxyFix found in werkzeug. Instead of counting the number of trusted proxies it peels away all the “trusted” IP-addresses until it arrives at the first untrusted one.


## Usage

```python
import proxyfix from impact_stack

# Flask
app.wsgi_app = proxyfix.ProxyFix.from_config(app.config.get).wrap(app.wsgi_app)

# Django
import functools
from django.conf import settings
from django.core.wsgi import wsgi_application

application = get_wsgi_application()
config_getter = functools.partial(getattr, settings)
application = proxyfix.ProxyFix.from_config(config_getter).wrap(application)
```
