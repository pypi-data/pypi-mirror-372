import requests

# from .models import Plan, Subscription
from .settings import ASKELL_ENDPOINT, ASKELL_SECRET_KEY
from .utils import get_customer_reference_from_user


class AskellClient:

    def __init__(self, token, endpoint=None):
        self.TOKEN = token
        if endpoint:
            self.ENDPOINT = endpoint

    def _build_url(self, path):
        return "{}{}".format(self.ENDPOINT, path)

    @property
    def _auth(self):
        return {
            "Authorization": "Api-Key {}".format(self.TOKEN)
        }

    def get_subscriptions(self, id=None):
        path = '/subscriptions/'
        if id: 
            path = "/subscriptions/{}/".format(id)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()

    def get_plans(self, id=None):
        path = '/plans/'
        if id: 
            path = "/plans/{}/".format(id)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()
    
    def make_payment(self, user, amount, currency, reference, description=None, payment_options=None):
        customer_reference = get_customer_reference_from_user(user)
        path = '/payments/'
        data = {
            "customer_reference": customer_reference,
            "amount": amount,
            "currency": currency,
            "reference": reference,
        }
        if description:
            data["description"] = description

        if payment_options:
            # check that only allowed keys in dict are "payment_processor" == "claim", claimtemplate, claimrule or payment_date:
            allowed_keys = ["payment_processor", "claimtemplate", "claimrule", "payment_date", "payor_id"]
            for key in payment_options.keys():
                if key not in allowed_keys:
                    raise ValueError(f"Invalid key '{key}' in payment options. Allowed keys are: {allowed_keys}")
                if key == "payment_processor":
                    if payment_options[key] not in ["claim",]:
                        raise ValueError(f"Invalid value '{payment_options[key]}' for key 'payment_processor'. Allowed values are: ['claim']")
            data["payment_options"] = payment_options

        response = requests.post(self._build_url(path), headers=self._auth, json=data)
        return response.json()
    
    def get_payment(self, uuid):
        path = '/payments/{}/'.format(uuid)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()

    def get_customer(self, user):
        customer_reference = get_customer_reference_from_user(user)
        path = '/customers/{}/'.format(customer_reference)
        response = requests.get(self._build_url(path), headers=self._auth)

        if response.status_code == 200:
            return {'status': 'success', 'response': response.json()}
        else:
            return {'status': 'error', 'message': "Could not get customer"}


    def create_customer(self, user):
        customer_reference = get_customer_reference_from_user(user)
        path = '/customers/'
        data = {
            "customer_reference": customer_reference,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        response = requests.post(self._build_url(path), headers=self._auth, json=data)

        if response.status_code < 300:
            return {'status': 'success', 'response': response.json()}
        else:
            return {'status': 'error', 'message': "Could not create customer"}


    def create_checkout(self, plan_variant_id, capture_only=False):
        path = '/checkout/'
        data = {
            "plan_variant_id": plan_variant_id,
            "capture_only": capture_only
        }
        response = requests.post(self._build_url(path), headers=self._auth, json=data)
        return response.json()


    def import_payment_method(self, user, payment_method_data):
        customer_reference = get_customer_reference_from_user(user)
        path = '/customers/paymentmethod/import/'
        data = {
            "customer_reference": customer_reference,
        }
        assert "token" in payment_method_data.keys(), "payment_method_data must include 'token'"
        assert "payment_processor_type" in payment_method_data.keys(), "payment_method_data must include 'payment_processor_type'"
        assert "card_info" in payment_method_data.keys(), "payment_method_data must include 'card_info'"
        assert "expiration_month" in payment_method_data.keys(), "payment_method_data must include 'expiration_month'"
        assert "expiration_year" in payment_method_data.keys(), "payment_method_data must include 'expiration_year'"

        data.update(**payment_method_data)
        
        response = requests.post(self._build_url(path), headers=self._auth, json=data)
        
        return response.json()


client = AskellClient(ASKELL_SECRET_KEY, endpoint=ASKELL_ENDPOINT)
