import asyncio
import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

F = TypeVar("F", bound=DeclarativeBase)
T = TypeVar("T", bound=BaseModel)
P = ParamSpec("P")


class ObjectMapper:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"It is not possible to create {cls.__name__} instance")

    # {from_class: {to_class: funс}}
    _mappers: dict[type, dict[type, Callable | None]] = {}

    @classmethod
    def register(
        cls,
        from_: type[F],
        to: type[T],
        *,
        func: Callable[[Concatenate[F, P]], T | Coroutine[Any, Any, T]] | None = None,
        override_existing: bool = False,
    ):
        """
        Registers a mapping function between a SQLAlchemy ORM class and a Pydantic model class.

        This method allows specifying a custom function that converts instances of the
        `from_` class (subclass of `DeclarativeBase`) into instances of the `to` class
        (subclass of `BaseModel`). If no function is provided, Pydantic's fallback
        mapping (`model_validate` with `from_attributes=True`) is used, provided that
        the Pydantic model is configured to allow attribute-based initialization.

        :param from_: The SQLAlchemy ORM class to map from. Must inherit from `DeclarativeBase`.
        :param to: The Pydantic model class to map to. Must inherit from `BaseModel`.
        :param func: Optional; a callable that takes an instance of `from_` and returns
        an instance of `to`, or an awaitable returning `to`.
        :param override_existing: If True mapping can be re-registered
        :return: The registered function if provided, otherwise a decorator to register a function.
        :raises TypeError: If `from_` is not a subclass of `DeclarativeBase` or `to` is not a subclass of `BaseModel`.
        :raises ValueError: If `to` does not have `model_config = ConfigDict(from_attributes=True)` and no custom function is provided.
        :raises KeyError: If mapping with `from_` and `to` already exists and ``override_existing`` is not ``True``.
        Notes
        -----
        - If a function is provided via `func`, it is used for mapping calls.
        - If no function is provided, the fallback mapping relies on Pydantic's
          `model_validate(from_, from_attributes=True)`, which requires that
          objects do not contain lazy-loaded attributes.
        - Can be used as a decorator to register a mapping function after method definition.
        """
        if not issubclass(from_, DeclarativeBase):
            raise TypeError(
                "from_ must be a class inheriting from sqlalchemy.orm.DeclarativeBase"
            )
        if not issubclass(to, BaseModel):
            raise TypeError("to_ must be a class inheriting from pydantic.BaseModel")

        if (
            (not override_existing)
            and from_ in cls._mappers
            and to in cls._mappers[from_]
        ):
            raise KeyError(
                f"A mapping from {from_.__name__} to {to.__name__} is already registered."
            )

        def decorator(f: Callable[[F], T | Awaitable[T]]):
            cls._mappers.setdefault(from_, {})[to] = f
            return f

        if func is not None:
            cls._mappers.setdefault(from_, {})[to] = func
            return func
        else:
            config = getattr(to, "model_config", None)
            if not (config and config.get("from_attributes", False)):
                raise ValueError(
                    f"Pydantic-model {to.__name__} doesn't have "
                    f"model_config = ConfigDict(from_attributes=True), "
                    f"and the custom mapping function has not been passed."
                )
            cls._mappers.setdefault(from_, {})[to] = None
        return decorator

    @classmethod
    def unregister(cls, from_: type[F], to: type[T]) -> None:
        """
        Removes a registered mapping between a SQLAlchemy ORM class and a Pydantic model class.

        :param from_: The SQLAlchemy ORM class of the mapping to remove.
        :param to: The Pydantic model class of the mapping to remove.
        """
        if from_ not in cls._mappers or to not in cls._mappers[from_]:
            raise KeyError(
                f"No mapping from {from_.__name__} to {to.__name__} registered."
            )
        cls._mappers[from_].pop(to)
        if not cls._mappers[from_]:
            cls._mappers.pop(from_)

    @classmethod
    def clear(cls) -> None:
        """
        Clears all registered mappings.
        """
        cls._mappers.clear()

    @classmethod
    def list_mappers(cls) -> list[tuple[type, type]]:
        """
        Returns a list of all registered mapping pairs.

        :return: List of tuples (from_class, to_class).
        """
        return [(f, t) for f, sub in cls._mappers.items() for t in sub]

    @classmethod
    async def map(cls, from_: F, to: type[T], **func_kwargs: Any) -> T:
        """
        Asynchronously maps a SQLAlchemy ORM object to a Pydantic model instance.

        This method converts the provided `from_` object (an instance of a class
        inheriting from `DeclarativeBase`) into an instance of the `to` class
        (subclass of `BaseModel`). The conversion is performed either via a
        registered custom mapping function or, if none is available, through
        Pydantic's fallback mechanism (`model_validate` with `from_attributes=True`).

        :param from_: A SQLAlchemy ORM object to be mapped.
        :param to: The Pydantic model class to map the object to.
        :param func_kwargs: ``Optional``, Keyword arguments to pass to the registered custom mapping function.
        Only keys listed in `func_kwargs` during registration will be used.
        :return: A Pydantic model instance resulting from the mapping.
        :raises KeyError: If no custom mapping function is registered for `to` and fallback mapping is not possible.

        Notes
        -----
        - If no mapping function is registered, fallback mapping uses
        - `to.model_validate(from_, from_attributes=True)`. The `from_` object
          must not contain lazy-loaded attributes to avoid unexpected database
          queries or `DetachedInstanceError`.
        """
        func = cls._mappers.get(type(from_), {}).get(to)

        if not func:
            # fallback
            return to.model_validate(from_, from_attributes=True)

        result = func(from_, **func_kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    @classmethod
    async def map_many(
        cls, from_items: Sequence[F], to: type[T], **func_kwargs: Any
    ) -> list[T]:
        """
        Asynchronously maps a SQLAlchemy ORM objects (Sequence) to a Pydantic model instances.

        This method converts the provided `from_` object (an instance of a class
        inheriting from `DeclarativeBase`) into an instance of the `to` class
        (subclass of `BaseModel`). The conversion is performed either via a
        registered custom mapping function or, if none is available, through
        Pydantic's fallback mechanism (`model_validate` with `from_attributes=True`).

        :param from_items: A Sequence of SQLAlchemy ORM objects to be mapped.
        :param to: The Pydantic model class to map the object to.
        :param func_kwargs: ``Optional``, Keyword arguments to pass to the registered custom mapping function.
        Only keys listed in `func_kwargs` during registration will be used.
        :return: A list of Pydantic model instances resulting from the mapping.
        :raises KeyError: If no custom mapping function is registered for `to` and fallback mapping is not possible.

        Notes
        -----
        - If no mapping function is registered, fallback mapping uses
        - `to.model_validate(from_, from_attributes=True)`. The `from_` object
          must not contain lazy-loaded attributes to avoid unexpected database
          queries or `DetachedInstanceError`.
        """
        if not from_items:
            return []

        func = cls._mappers.get(type(from_items[0]), {}).get(to)

        if not func:
            # fallback
            return [
                to.model_validate(item, from_attributes=True) for item in from_items
            ]

        first_res = func(from_items[0], **func_kwargs)
        if inspect.isawaitable(first_res):
            coros = [first_res]
            coros.extend([func(item, **func_kwargs) for item in from_items[1:]])
            return list(await asyncio.gather(*coros))
        else:
            res = [first_res]
            res.extend([func(item, **func_kwargs) for item in from_items[1:]])
            return res
