# django-askell
Áskell integration for Django and Wagtail (optional)

<a href="https://github.com/overcastsoftware/django-askell/actions">
    <img src="https://github.com/overcastsoftware/django-askell/workflows/django-askell%20CI/badge.svg" alt="Build Status" />
</a>


## Installation

```shell
pip install django-askell
```

Add the app to your `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ... other apps
    
    'askell',

    # ... other apps
]
```

Add the app urls to your project `urls.py`:

```python
from django.urls import path, include

from askell.urls import urls as askell_urls

urlpatterns = [
    # ... your other urls
    path('askell/', include(askell_urls)),
    # ... more urls
]
```

Then go to Áskell, create a public/private key pair and add these keys to your settings file or environment in your project:
```python
ASKELL_PUBLIC_KEY = 'my-public-key'
ASKELL_SECRET_KEY = 'my-secret-key'
```

To complete your setup, it is recommended to set up a webhook in Áskell's dashboard pointing to your website's URL. If your website has the domain `https://example.com` and you have added the app urls to your project, then the view that receives the webhooks is located at `https://example.com/askell/webhook/`.

Create your webhook, and then obtain your webhook secret and put it in your settings file or environment in your project:

```python
ASKELL_WEBHOOK_SECRET = 'my-secret'
```

## Webhook handlers

You can register new webhook handlers if you want to implement custom logic when something happens in Áskell.
These are the default webhook handlers:

```
askell.webhook_handlers.payment_created
askell.webhook_handlers.payment_changed
```

Registering a new handler is simple:

```python
from askell.webhooks import register_webhook_handler

@register_webhook_handler
def payment_settled(request, event, data):
    from .models import Payment
    if event == 'payment.changed':
        if data['state'] == 'settled':
            # do something here
    return True
```

## TODO

- [x] Document webhook handlers
- [ ] Document views
- [ ] Implement subscription handling

## Release notes

### Version 0.1.19
* Adding payment method import method

### Version 0.1.7
* Fixed a bug in creating a customer

### Version 0.1.6
* Added support for multiple states

### Version 0.1.5
* Fixed a bug with imports

### Version 0.1.4
* Fixed a bug in the Payment detail view

### Version 0.1.3
* Fixed a bug in webhook handler

### Version 0.1.2
* Added logging mechanism for debugging

### Version 0.1.1
* Changed the way webhook handlers are imported and documented

### Version 0.1
* Support for creating Payment objects
* Support for webhooks processing and verification
* Default webhook handlers for payment created, and changed
