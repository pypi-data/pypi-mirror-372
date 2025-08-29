from typing import Type

from tp_interfaces.domain.interfaces import DomainProducer


def _get_stub() -> Type[DomainProducer]:
    from tp_interfaces.domain.stub import StubDomainProducer
    return StubDomainProducer


DOMAIN_FACTORY = _get_stub()
