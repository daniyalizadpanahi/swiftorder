import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from orders.models import Order

def initiate_payment(request):
    amount = 1000  # مبلغ به ریال
    callback_url = request.build_absolute_uri(
        reverse("verify_payment")
    )  # آدرس برگشتی بعد از پرداخت
    # داده‌ها برای ارسال به زرین پال
    data = {
        "MerchantID": settings.ZARINPAL_MERCHANT_ID,
        "Amount": amount,
        "CallbackURL": callback_url,
    }

    # ارسال درخواست به زرین پال
    response = requests.post(settings.ZARINPAL_API_URL, data=data)
    result = response.json()

    if result["Status"] == 100:
        # کاربر به صفحه پرداخت هدایت می‌شود
        return HttpResponseRedirect(
            f'https://www.zarinpal.com/pg/StartPay/{result["Authority"]}'
        )
    else:
        return JsonResponse({"error": "Payment failed"}, status=400)


def verify_payment(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    try:
        order = Order.objects.get(payment_id=authority)  # پیدا کردن سفارش با استفاده از payment_id
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if status == 'OK':
        # تایید پرداخت از زرین پال
        data = {
            'MerchantID': settings.ZARINPAL_MERCHANT_ID,
            'Authority': authority,
        }
        
        # ارسال درخواست تایید به زرین پال
        response = requests.post('https://api.zarinpal.com/pg/rest/WebGate/PaymentVerification.json', data=data)
        result = response.json()
        
        if result['Status'] == 100:
            # پرداخت با موفقیت انجام شده است
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
