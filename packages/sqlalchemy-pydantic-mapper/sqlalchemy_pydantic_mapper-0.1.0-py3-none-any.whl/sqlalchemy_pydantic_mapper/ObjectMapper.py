import inspect
from typing import Awaitable, Callable

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


class ObjectMapper:
    # {from_class: {to_class: func}}
    _mappers: dict[type, dict[type, Callable | None]] = {}

    @classmethod
    def register[F: DeclarativeBase, T: BaseModel](
        cls,
        from_: type[F],
        to_: type[T],
        *,
        func: Callable[[F], T | Awaitable[T]] | None = None,
    ):
        if not issubclass(from_, DeclarativeBase):
            raise TypeError(
                "from_ must be a class inheriting from sqlalchemy.orm.DeclarativeBase"
            )
        if not issubclass(to_, BaseModel):
            raise TypeError("to_ must be a class inheriting from pydantic.BaseModel")

        def decorator(f: Callable[[F], T]):
            cls._mappers.setdefault(from_, {})[to_] = f
            return f

        if func is not None:
            cls._mappers.setdefault(from_, {})[to_] = func
            return func
        else:
            config = getattr(to_, "model_config", None)
            if not (config and config.get("from_attributes", False)):
                raise ValueError(
                    f"Pydantic-model {to_.__class__} doesn't have "
                    f"model_config = ConfigDict(from_attributes=True), "
                    f"and the custom mapping function has not been passed."
                )

        return decorator

    @classmethod
    async def map[F: DeclarativeBase, T: BaseModel](cls, from_: F, to: type[T]) -> T:
        # noinspection PyTypeChecker
        func = cls._mappers.get(from_.__class__, {}).get(to)
        if not func:
            return to.model_validate(from_, from_attributes=True)
        result = func(from_)
        if inspect.isawaitable(result):
            return await result
        return result
