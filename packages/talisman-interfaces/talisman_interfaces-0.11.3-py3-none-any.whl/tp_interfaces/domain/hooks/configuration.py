from typing import Type

from tp_interfaces.abstract import ModelTypeFactory
from tp_interfaces.domain.interfaces import AbstractDomainChangeHook


def _get_update_tdm_hook() -> Type[AbstractDomainChangeHook]:
    from .tdm_factory import UpdateTDMDefaultDomainHook
    return UpdateTDMDefaultDomainHook


def _get_set_default_domain_hook() -> Type[AbstractDomainChangeHook]:
    from .default_domain import SetDefaultDomainHook
    return SetDefaultDomainHook


DOMAIN_CHANGE_HOOKS = ModelTypeFactory({
    'tdm': _get_update_tdm_hook,
    'default': _get_set_default_domain_hook
})
