from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from limits.storage import MemoryStorage, RedisStorage, MemcachedStorage
from rest_framework import viewsets, serializers, views
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from django_ratelimiter import ratelimit


@ratelimit("5/minute")
def defaults(_: HttpRequest, count: int) -> HttpResponse:
    return HttpResponse(f"{count}")


@ratelimit("5/minute", key="user")
def by_string_key(request: HttpRequest) -> HttpResponse:
    return HttpResponse(request.user.pk)


@ratelimit("5/minute", key=lambda r: r.user.get_username())
def by_func_key(request: HttpRequest) -> HttpResponse:
    return HttpResponse(request.user.pk)


@require_http_methods(["POST", "PUT", "GET"])
@ratelimit("5/minute", methods=["POST", "PUT"])
def by_method(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@ratelimit("5/minute", strategy="fixed-window-elastic-expiry")
def fixed_window_elastic_expiry(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@ratelimit("1/minute", response=HttpResponse(status=418))
def teapot(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@method_decorator(ratelimit("1/minute"), name="dispatch")
class TestView(View):
    def get(self, _: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    def post(self, _: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")


memory_storage = MemoryStorage()
redis_storage = RedisStorage(uri="redis://localhost:6379/0")
memcached_storage = MemcachedStorage(uri="memcached://localhost:11211")


@ratelimit("5/minute", storage=memory_storage)
def memory(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@ratelimit("5/minute", storage=redis_storage)
def redis(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@ratelimit("5/minute", storage=memcached_storage)
def memcached(_: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@api_view(["GET"])
@ratelimit("5/minute")
def drf_api_view(_: Request) -> Response:
    return Response({"hello": "world"})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


@method_decorator(ratelimit("5/minute"), name="dispatch")
class TestViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@method_decorator(ratelimit("5/minute"), name="dispatch")
class TestDRFView(views.APIView):
    def get(self, _: Request) -> Response:
        return Response("200")
