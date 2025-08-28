import hmac
import base64
import json
import logging
import hashlib
import requests

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.utils.translation import gettext as _
from rest_framework.views import APIView
from rest_framework.response import Response

from .settings import ASKELL_WEBHOOK_SECRET, ASKELL_ENDPOINT, ASKELL_SECRET_KEY
from .utils import get_customer_reference_from_user
from .models import Payment
from .webhooks import run_webhook_handlers

logger = logging.getLogger('django-askell')


WEBHOOK_SECRET = ASKELL_WEBHOOK_SECRET.encode()
WEBHOOK_DIGEST_TYPE = 'sha512'

# also available at `thorn.utils.hmac.verify`
def verify(hmac_header, digest_method, secret, message):
    logger.debug(f'''Verifying webhook signature:
                    HMAC header: {hmac_header}
                    Digest method: {digest_method}
                    Secret: {secret}
                    Message: {message}
                ''')
    digestmod = getattr(hashlib, digest_method)
    signed = base64.b64encode(
        hmac.new(secret, message, digestmod).digest(),
    ).strip()
    return hmac.compare_digest(signed, hmac_header)


class WebhookHandlerView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        digest = request.META.get('HTTP_HOOK_HMAC').encode()
        event = request.META.get('HTTP_HOOK_EVENT')
        body = request.body
        error_message = 'Could not verify webhook signature. Check your webhook secret and digest type.'

        logger.debug(f'''Webhook received:
                     Event: {event}
                     Body: {body}
                     Digest: {digest}''')

        if verify(digest, WEBHOOK_DIGEST_TYPE, WEBHOOK_SECRET, body):
            payload = json.loads(body)
            event = payload['event']
            data = payload['data']

            if run_webhook_handlers(request, event, data):
                return Response({'status': 'success'}, status=200)
            else:
                error_message = 'Could not run webhook handlers.'
        else:
            logger.warning(f'Webhook signature verification failed: {error_message}')

        return Response({'status': 'error', 'error': error_message}, status=400)


@method_decorator(login_required, name='dispatch')
class UpdateCardView(APIView):


    def post(self, request, format=None):

        headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}
        
        customer_reference = get_customer_reference_from_user(request.user)

        post_data = {
            "customer_reference": customer_reference,
            "token": request.data['token'],
        }

        url = f"{ASKELL_ENDPOINT}/customers/paymentmethod/"
        r = requests.post(url, headers=headers, json=post_data)
        response = r.json()

        if r.status_code < 300:
            return Response({'status': 'success', 'response': response})
        else:
            return Response({'status': 'error', 'message': response['error']}, status=r.status_code)


@method_decorator(login_required, name='dispatch')
class TransactionReceiptView(APIView):

    def get(self, request, uuid=None, format=None):

        try:

            headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}

            url = f"{ASKELL_ENDPOINT}/transactions/{uuid}/receipt/"
            r = requests.get(url, headers=headers)
            
            pdf_response = r.json()

            if r.status_code == 200:
                response = HttpResponse(base64.b64decode(pdf_response['receipt']), content_type='application/pdf;')
                response['Content-Disposition'] = f'inline; filename={pdf_response["filename"]}.pdf'
                return response
            else:
                return Response({'status': 'error', 'message': pdf_response['error']}, status=r.status_code)
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': f"{_('Server error. Please try again later.')} {e} {pdf_response}"}, status=r.status_code)


@method_decorator(login_required, name='dispatch')
class CustomerView(APIView):

    def get(self, request):

        try:
            headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}
            customer_reference = get_customer_reference_from_user(request.user)
            
            if customer_reference:
                url = f"{ASKELL_ENDPOINT}/customers/{customer_reference}/"
                r = requests.get(url, headers=headers)
                response = r.json()

                if r.status_code == 200:
                    return Response({'status': 'success', 'response': response})
                else:
                    return Response({'status': 'error', 'message': response['error']}, status=r.status_code)
            else:
                return Response({'status': 'success', 'response': {}})
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': _('Server error. Please try again later.')}, status=400)
        
    
    def post(self, request, format=None):
        try:
            headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}
            customer_reference = get_customer_reference_from_user(request.user)

            post_data = {
                "customer_reference": customer_reference,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
            }

            url = f"{ASKELL_ENDPOINT}/customers/"
            r = requests.post(url, headers=headers, json=post_data)
            response = r.json()

            if r.status_code < 300:
                return Response({'status': 'success', 'response': response})
            else:
                return Response({'status': 'error', 'message': response['error']}, status=r.status_code)
            
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': _('Server error. Please try again later.')}, status=r.status_code)
        
    

@method_decorator(login_required, name='dispatch')
class PaymentMethodView(APIView):
    
    def post(self, request, format=None):
        customer_reference = get_customer_reference_from_user(request.user)
        headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}
        c_response = requests.get(f"{ASKELL_ENDPOINT}/customers/{customer_reference}/", headers=headers)
        if c_response.status_code == 404:
            s = CustomerView().post(request, format=None)
            if s.status_code > 299:
                return s

        return UpdateCardView().post(request, format=None)


@method_decorator(login_required, name='dispatch')
class PaymentView(APIView):

    def get(self, request, uuid=None):
        try:
            payment = Payment.objects.filter(uuid=uuid).first()
            if payment:
                return Response({'status': 'success', 'response': payment.as_dict()})
            else:
                return Response({'status': 'error', 'response': {}})
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': _('Server error. Please try again later.')}, status=500)

    def post(self, request):
        try:
            headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}
            customer_reference = get_customer_reference_from_user(request.user)

            if customer_reference:
                url = f"{ASKELL_ENDPOINT}/customers/{customer_reference}/paymentmethod/"
                r = requests.post(url, headers=headers, json=request.data)
                    
                response = r.json()

                if r.status_code == 201:
                    payment_data = {key: response[key] for key in Payment.KEYS_TO_COPY}
                    payment_data['user'] = request.user

                    payment, created = Payment.objects.get_or_create(**payment_data)
                    return Response({'status': 'success', 'response': payment.as_dict()}, status=201)
                else:
                    return Response({'status': 'error', 'message': response['error']}, status=r.status_code)
            else:
                return Response({'status': 'success', 'response': {}})
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': _('Server error. Please try again later.')}, status=r.status_code)
        

@method_decorator(login_required, name='dispatch')
class CheckoutView(APIView):

    def post(self, request):
        try:
            headers = {"Authorization": f"Api-Key {ASKELL_SECRET_KEY}"}

            post_data = {
                "plan": request.data['plan'],
                "capture_only": request.data.get('capture_only', False),
            }

            url = f"{ASKELL_ENDPOINT}/checkouts/"
            r = requests.post(url, headers=headers, json=post_data)
            response = r.json()

            if r.status_code < 300:
                return Response({'status': 'success', 'response': response})
            else:
                return Response({'status': 'error', 'message': response['error']}, status=r.status_code)

        except Exception as e:
            return Response({'status': 'error', 'message': _('Server error. Please try again later.')}, status=r.status_code)