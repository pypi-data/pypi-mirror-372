from dataclasses import dataclass

from tp_interfaces.domain.abstract import AbstractNERCBasedType, NERCRegexp


@dataclass(frozen=True)
class NERCBasedType(AbstractNERCBasedType):
    _regexp: tuple[NERCRegexp, ...] = tuple()
    _black_regexp: tuple[NERCRegexp, ...] = tuple()
    _pretrained_nerc_models: tuple[str, ...] = tuple()
    _dictionary: tuple[str, ...] = tuple()
    _black_list: tuple[str, ...] = tuple()

    def __post_init__(self):
        if self._regexp:
            object.__setattr__(self, '_regexp', tuple(map(self._convert_to_regexp, self._regexp)))
        if self._black_regexp:
            object.__setattr__(self, '_black_regexp', tuple(map(self._convert_to_regexp, self._black_regexp)))

        for attr in ['_regexp', '_black_regexp', '_pretrained_nerc_models', '_dictionary', '_black_list']:
            if isinstance(getattr(self, attr), list):
                object.__setattr__(self, attr, tuple(getattr(self, attr)))

    @property
    async def regexp(self) -> tuple[NERCRegexp, ...]:
        return self._regexp

    @property
    async def black_regexp(self) -> tuple[NERCRegexp, ...]:
        return self._black_regexp

    @property
    async def pretrained_nerc_models(self) -> tuple[str, ...]:
        return self._pretrained_nerc_models

    @property
    async def dictionary(self) -> tuple[str, ...]:
        return self._dictionary

    @property
    async def black_list(self) -> tuple[str, ...]:
        return self._black_list

    @staticmethod
    def _convert_to_regexp(obj) -> NERCRegexp:
        if isinstance(obj, NERCRegexp):
            return obj
        if isinstance(obj, dict):
            return NERCRegexp(**obj)
        raise ValueError
