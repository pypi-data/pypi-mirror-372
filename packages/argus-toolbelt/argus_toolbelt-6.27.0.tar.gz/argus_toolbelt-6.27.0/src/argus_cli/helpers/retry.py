from typing import Callable, Iterable, Dict, Any, Optional, Type

from argus_cli.helpers.log import log


def retry(
    func: Callable,
    args: Optional[Iterable[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    exception_classes: Iterable[Type[Exception]] = None,
    max_retries: int = 0,
):
    """
    Retries calling a function up to a maximum number of attempts.

    :param func: function to retry
    :param args: positional arguments for the function
    :param kwargs: keyword arguments for the function
    :param exception_classes: iterable of exceptions to retry on.
    :param max_retries: maximum number of retries (mot including the initial call)
    :return: the return value of ``func(*args, **kwargs)``
    """
    args = args or tuple()
    kwargs = kwargs or dict()
    exception_classes = exception_classes or (Exception,)
    for try_ in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if (
                any(isinstance(e, exc) for exc in exception_classes)
                and try_ < max_retries
            ):
                log.warning(
                    f"retry: attempt({try_+1}/{max_retries}) failed, retrying. function={func}, args={args}, kwargs={kwargs}. Error: {e}."
                )
                continue
            raise
