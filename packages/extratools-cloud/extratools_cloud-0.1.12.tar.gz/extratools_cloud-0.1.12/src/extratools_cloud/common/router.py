from abc import ABC, abstractmethod
from collections.abc import Iterable
from logging import getLogger
from typing import Any, cast

logger = getLogger(__name__)


class BaseRouter[RT: Any, TT: Any](ABC):
    def __init__(
        self,
        *,
        default_target_resource: RT,
    ) -> None:
        self._default_target_resource: RT = default_target_resource

        self.targets: dict[TT, RT] = {}

    def register_targets(
        self,
        resource: RT,
        targets: Iterable[TT],
    ) -> None:
        targets = list(targets)
        if not targets:
            return

        logger.info(f"Registering resource {resource} for targets {targets}")

        self.targets.update(dict.fromkeys(targets, resource))

    @abstractmethod
    def _route_to_resource[DT: Any](
        self,
        data: Iterable[DT],
        resource: RT,
        target: TT,
    ) -> Iterable[Any]:
        ...

    def route_to_target[DT: Any](
        self,
        data: Iterable[DT],
        target: TT,
    ) -> Iterable[Any]:
        resource: RT = cast("RT", self.targets.get(target, self._default_target_resource))

        logger.info(f"Routing to resource {resource} for target {target}")

        return self._route_to_resource(data, resource, target)
