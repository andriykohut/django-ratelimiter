import sys

if sys.version_info < (3, 10):
    from typing_extensions import Concatenate, ParamSpec
else:
    from typing import Concatenate, ParamSpec

from typing import Callable

from django.http import HttpRequest, HttpResponse

P = ParamSpec("P")

ViewFunc = Callable[Concatenate[HttpRequest, P], HttpResponse]
