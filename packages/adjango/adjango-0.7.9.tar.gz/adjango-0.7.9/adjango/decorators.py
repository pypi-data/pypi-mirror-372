# decorators.py
from __future__ import annotations

import json
import logging
from functools import wraps
from time import time
from typing import Any, Callable, Optional

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, QueryDict, RawPostDataException
from django.shortcuts import redirect

from adjango.conf import (
    ADJANGO_CONTROLLERS_LOGGER_NAME,
    ADJANGO_CONTROLLERS_LOGGING,
    ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION,
)
from adjango.utils.common import traceback_str


def admin_label(label: str):
    def decorator(func):
        func.label = label
        return func

    return decorator


def task(logger: Optional[str] = None):
    """
    Decorator for Celery tasks that logs start and end of task execution and its errors.

    :param logger: Logger name for logging. If not provided, logging will not be performed.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = None
            if logger:
                log = logging.getLogger(logger)
                log.info(f'Start executing task: {func.__name__}\n{args}\n{kwargs}')
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                log.critical(f'Error executing task: {func.__name__}')
                log.critical(traceback_str(e))
                raise e
            if log:
                log.info(f'End executing task: {func.__name__}\n{args}\n{kwargs}')
            return result

        return wrapper

    return decorator


def force_data(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for merging data from POST, GET and JSON request body.

    :param fn: Function to be wrapped.

    :return: Function with merged data from different parts of request.

    @usage:
        @force_data
        def my_view(request):
            print(request.data)
    """

    @wraps(fn)
    def _wrapped_view(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not hasattr(request, 'data'):
            request.data = {}
        request.data.update(request.POST.dict() if isinstance(request.POST, QueryDict) else request.POST)
        request.data.update(request.GET.dict() if isinstance(request.GET, QueryDict) else request.GET)
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            if isinstance(json_data, dict):
                request.data.update(json_data)
        except (ValueError, TypeError, UnicodeDecodeError, RawPostDataException):
            pass
        return fn(request, *args, **kwargs)

    return _wrapped_view


def controller(
    name: str | None = None,
    logger: Optional[str] = None,
    log_name: bool = True,
    log_time: bool = False,
    auth_required: bool = False,
    not_auth_redirect: str = settings.LOGIN_URL,
) -> Callable[..., Any]:
    """
    Synchronous controller with logging, authentication checking and exception handling.

    :param name: Controller name.
    :param logger: Logger name for writing messages.
    :param log_name: Log controller name.
    :param log_time: Log controller execution time.
    :param auth_required: Whether to check user authentication.
    :param not_auth_redirect: URL for redirect if user is not authenticated.

    :return: Synchronous controller with logging and exception handling.

    @usage:
        @controller
        def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def inner(request: WSGIRequest, *args: Any, **kwargs: Any) -> Any:
            log = logging.getLogger(logger or ADJANGO_CONTROLLERS_LOGGER_NAME)
            fn_name = name or fn.__name__
            start_time = None
            if log_name or (log_name is None and ADJANGO_CONTROLLERS_LOGGING):
                log.info(f'Ctrl: {request.method} | {fn_name}')
            if log_time:
                start_time = time()
            if auth_required and not request.user.is_authenticated:
                return redirect(not_auth_redirect)
            if settings.DEBUG:
                result = fn(request, *args, **kwargs)
                if log_time and start_time is not None:
                    end_time = time()
                    elapsed_time = end_time - start_time
                    log.info(f'Execution time {fn_name}: {elapsed_time:.2f} seconds')
                return result
            else:
                try:
                    result = fn(request, *args, **kwargs)
                    if log_time and start_time is not None:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f'Execution time {fn_name}: {elapsed_time:.2f} seconds')
                    return result
                except Exception as e:
                    log.critical(f'ERROR in {fn_name}: {traceback_str(e)}', exc_info=True)
                    if hasattr(settings, 'ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION'):
                        handling_function = ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION
                        if callable(handling_function):
                            handling_function(fn_name, request, e, *args, **kwargs)
                    raise e

        return inner

    return decorator
