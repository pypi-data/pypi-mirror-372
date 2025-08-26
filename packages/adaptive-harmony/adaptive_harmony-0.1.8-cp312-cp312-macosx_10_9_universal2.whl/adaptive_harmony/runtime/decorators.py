from typing import TypeVar, Callable, Any, overload

from adaptive_harmony.runtime.context import RecipeContext
from adaptive_harmony.runtime.data import InputConfig

IN = TypeVar("IN", bound=InputConfig)


@overload
def recipe_main(func: Callable[[IN, RecipeContext], Any]): ...


@overload
def recipe_main(func: Callable[[RecipeContext], Any]): ...


def recipe_main(func):
    func.is_recipe_main = True
    return func
