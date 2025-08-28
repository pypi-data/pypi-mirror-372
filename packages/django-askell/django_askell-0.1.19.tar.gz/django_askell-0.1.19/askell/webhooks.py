import logging

logger = logging.getLogger('django-askell')


WEBHOOK_HANDLERS = []

def get_webhook_handlers():
    return WEBHOOK_HANDLERS


def register_webhook_handler(func):
    if func not in WEBHOOK_HANDLERS:
        WEBHOOK_HANDLERS.append(func)
    return func


def run_webhook_handlers(request, event, data):
    for func in WEBHOOK_HANDLERS:
        logger.debug(f'Running webhook handler: {func.__name__}')
        if not func(request, event, data):
            logger.debug(f'Webhook handler {func.__name__} returned False.')
            return False
    logger.debug(f'Webhook handler {func.__name__} returned True.')
    return True