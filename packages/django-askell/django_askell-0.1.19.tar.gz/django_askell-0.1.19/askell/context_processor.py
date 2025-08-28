from .settings import ASKELL_PUBLIC_KEY


def settings(request):
    return {
        'ASKELL_PUBLIC_KEY': ASKELL_PUBLIC_KEY
    }

