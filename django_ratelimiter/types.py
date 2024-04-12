import sys

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, Concatenate
else:
    from typing import ParamSpec, Concatenate

from typing import Callable
from django.http import HttpRequest, HttpResponse

P = ParamSpec("P")

ViewFunc = Callable[Concatenate[HttpRequest, P], HttpResponse]
