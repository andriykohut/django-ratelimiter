from typing import ParamSpec, Callable, Concatenate
from django.http import HttpRequest, HttpResponse

P = ParamSpec("P")

ViewFunc = Callable[Concatenate[HttpRequest, P], HttpResponse]
