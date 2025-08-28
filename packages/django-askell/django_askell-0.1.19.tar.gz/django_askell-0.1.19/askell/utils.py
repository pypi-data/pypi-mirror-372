from .settings import ASKELL_CUSTOMER_REFERENCE_USER_FIELD


def get_customer_reference_from_user(user):
    reference_field = getattr(user, ASKELL_CUSTOMER_REFERENCE_USER_FIELD)
    if callable(reference_field):
        return reference_field()
    else:
        return reference_field
