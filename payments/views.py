import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from orders.models import Order

# TODO This code is not complete and needs a payment panel to be reviewed.

def initiate_payment(request):
    amount = 1000
    callback_url = request.build_absolute_uri(
        reverse("verify_payment")
    )
    data = {
        "MerchantID": settings.ZARINPAL_MERCHANT_ID,
        "Amount": amount,
        "CallbackURL": callback_url,
    }

    response = requests.post(settings.ZARINPAL_API_URL, data=data)
    result = response.json()

    if result["Status"] == 100:
        return HttpResponseRedirect(
            f'https://www.zarinpal.com/pg/StartPay/{result["Authority"]}'
        )
    else:
        return JsonResponse({"error": "Payment failed"}, status=400)


def verify_payment(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    try:
        order = Order.objects.get(payment_id=authority)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if status == 'OK':
        data = {
            'MerchantID': settings.ZARINPAL_MERCHANT_ID,
            'Authority': authority,
        }
        
        response = requests.post('https://api.zarinpal.com/pg/rest/WebGate/PaymentVerification.json', data=data)
        result = response.json()
        
        if result['Status'] == 100:
            order.payment_status = 'paid'
            order.status = 'completed'
            order.save()
            return JsonResponse({'message': 'Payment successful!'}, status=200)
        else:
            order.payment_status = 'failed'
            order.save()
            return JsonResponse({'error': 'Payment verification failed'}, status=400)
    else:
        order.payment_status = 'canceled'
        order.save()
        return JsonResponse({'error': 'Payment failed or cancelled'}, status=400)
