import functools
import sys
import warnings

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:

    def deprecated(reason="This function is deprecated"):
        """Custom deprecated decorator for Python versions < 3.13"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                warnings.warn(f"{func.__name__} is deprecated. {reason}", category=DeprecationWarning, stacklevel=2)
                return func(*args, **kwargs)

            return wrapper

        return decorator
