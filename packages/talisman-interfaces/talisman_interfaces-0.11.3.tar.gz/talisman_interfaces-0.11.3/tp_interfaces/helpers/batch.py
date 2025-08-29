from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional, Sequence, Tuple

from tp_interfaces.abstract import ImmutableBaseModel

ConfigurableMessageProcessor = Callable[[Sequence[Any], ImmutableBaseModel], Tuple[Any, ...]]
AsyncConfigurableMessageProcessor = Callable[[Sequence[Any], ImmutableBaseModel], Coroutine]


class AbstractModelInput(ImmutableBaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_message(self) -> Any:
        pass

    @abstractmethod
    def get_config(self) -> Optional[ImmutableBaseModel]:
        pass


def batch_process_inputs(inputs: Sequence[AbstractModelInput], processor: ConfigurableMessageProcessor) \
        -> Tuple[Any, ...]:
    config2messages: Dict[ImmutableBaseModel, List[Tuple[int, Any]]] = defaultdict(list)
    for i, inp in enumerate(inputs):  # group messages by configs
        config2messages[inp.get_config()].append((i, inp.get_message()))

    outputs: List[Any] = [None] * len(inputs)  # prepare output to preserve messages order
    for config, messages_with_indicies in config2messages.items():  # batch process strings with response order guaranteed
        indices, messages = zip(*messages_with_indicies)
        indices: Iterable[int]
        for idx, output in zip(indices, processor(messages, config)):
            outputs[idx] = output

    return tuple(outputs)


async def async_batch_process_inputs(inputs: Sequence[AbstractModelInput], processor: AsyncConfigurableMessageProcessor) \
        -> Tuple[Any, ...]:
    config2messages: Dict[ImmutableBaseModel, List[Tuple[int, Any]]] = defaultdict(list)
    for i, inp in enumerate(inputs):  # group messages by configs
        config2messages[inp.get_config()].append((i, inp.get_message()))

    outputs: List[Any] = [None] * len(inputs)  # prepare output to preserve messages order
    for config, messages_with_indicies in config2messages.items():  # batch process strings with response order guaranteed
        indices, messages = zip(*messages_with_indicies)
        indices: Iterable[int]

        for idx, output in zip(indices, await processor(messages, config)):
            outputs[idx] = output

    return tuple(outputs)
