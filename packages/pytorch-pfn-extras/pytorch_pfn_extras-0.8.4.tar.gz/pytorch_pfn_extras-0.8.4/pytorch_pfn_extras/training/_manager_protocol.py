from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    runtime_checkable,
)

import torch
from typing_extensions import Protocol

if TYPE_CHECKING:
    from pytorch_pfn_extras import reporting, writing
    from pytorch_pfn_extras.training import trigger as trigger_module
    from pytorch_pfn_extras.training.extension import Extension


class ExtensionsManagerProtocol(Protocol):
    @property
    def iteration(self) -> int: ...

    @property
    def epoch(self) -> int: ...

    @property
    def epoch_detail(self) -> float: ...

    @property
    def _iters_per_epoch(self) -> int: ...

    @property
    def models(self) -> Mapping[str, torch.nn.Module]: ...

    @property
    def raw_models(self) -> Mapping[str, torch.nn.Module]: ...

    @property
    def optimizers(self) -> Mapping[str, torch.optim.Optimizer]: ...

    @property
    def elapsed_time(self) -> float: ...

    @property
    def is_before_training(self) -> bool: ...

    @property
    def stop_trigger(self) -> bool: ...

    @property
    def _stop_trigger(self) -> "trigger_module.Trigger": ...

    @property
    def out(self) -> str: ...

    @property
    def writer(self) -> Optional["writing.Writer"]: ...

    @property
    def reporter(self) -> "reporting.Reporter": ...

    def get_extension(self, name: str) -> "Extension": ...

    @property
    def observation(self) -> "reporting.Observation": ...


@runtime_checkable
class StateObjectProtocol(Protocol):
    def state_dict(self) -> Dict[str, Any]: ...

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None: ...
