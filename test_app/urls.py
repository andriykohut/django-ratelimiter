"""
URL configuration for test_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from test_app import views

router = DefaultRouter()
router.register(r"drf/viewset", views.TestViewSet, basename="viewset")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("defaults/<int:count>/", views.defaults, name="defaults"),
    path("by-string-key/", views.by_string_key, name="by_string_key"),
    path("by-func-key/", views.by_func_key, name="by_func_key"),
    path("by-method/", views.by_method, name="by_method"),
    path(
        "fixed-window-elastic-expiry/",
        views.fixed_window_elastic_expiry,
        name="fixed_window_elastic_expiry",
    ),
    path("teapot/", views.teapot, name="teapot"),
    path("cbv/", views.TestView.as_view()),
    path("storage/redis/", views.redis, name="redis_storage"),
    path("storage/memory/", views.memory, name="memory_storage"),
    path("storage/memcached/", views.memcached, name="memcached_storage"),
    path("drf/api-view/", views.drf_api_view, name="drf_api_view"),
    path("drf/view/", views.TestDRFView.as_view(), name="drf_view"),
    *router.urls,
]
