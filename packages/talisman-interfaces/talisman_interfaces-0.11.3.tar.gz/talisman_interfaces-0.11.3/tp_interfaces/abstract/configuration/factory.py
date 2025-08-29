from typing import Callable, Dict, Generic, ItemsView, TypeVar

_Value = TypeVar('_Value')


class ModelTypeFactory(Dict[str, _Value], Generic[_Value]):
    def __init__(self, items: Dict[str, Callable[[], _Value]]) -> None:
        super().__init__(items)

    def __getitem__(self, k: str) -> _Value:
        return super().__getitem__(k)()

    def items(self) -> ItemsView[str, Callable[[], _Value]]:
        return super().items()
