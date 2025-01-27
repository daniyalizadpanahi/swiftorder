import redis
import os
from django.http import HttpResponse

r = redis.StrictRedis(host='redis_cache', port=6379, db=0, decode_responses=True)

def rate_limit_middleware(get_response):
    def middleware(request):
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f"rate_limit:{ip}"
        request_limit = 20
        time_window = 60

        request_count = r.get(cache_key)

        if request_count and int(request_count) >= request_limit:
            return HttpResponse('Rate limit exceeded', status=429)

        p = r.pipeline()
        p.incr(cache_key)
        p.expire(cache_key, time_window)
        p.execute()

        return get_response(request)

    return middleware
