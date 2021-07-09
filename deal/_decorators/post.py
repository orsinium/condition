from typing import Callable, TypeVar

from .._exceptions import PostContractError
from .._types import ExceptionType
from .base import Base


_CallableType = TypeVar('_CallableType', bound=Callable)


class Post(Base[_CallableType]):
    """
    Check contract (validator) after function processing.
    Validate output result.
    """
    __slots__ = ['validator', 'validate', 'exception', 'function']

    @classmethod
    def _default_exception(cls) -> ExceptionType:
        return PostContractError

    def patched_function(self, *args, **kwargs):
        """
        Step 3. Wrapped function calling.
        """
        result = self.function(*args, **kwargs)
        self.validate(result)
        return result

    async def async_patched_function(self, *args, **kwargs):
        """
        Step 3. Wrapped function calling.
        """
        result = await self.function(*args, **kwargs)
        self.validate(result)
        return result

    def patched_generator(self, *args, **kwargs):
        """
        Step 3. Wrapped function calling.
        """
        for result in self.function(*args, **kwargs):
            self.validate(result)
            yield result
