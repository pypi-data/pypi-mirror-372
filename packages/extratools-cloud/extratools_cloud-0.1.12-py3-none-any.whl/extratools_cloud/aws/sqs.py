import json
from collections.abc import Iterable
from secrets import token_hex
from typing import Any, Literal, cast, override
from uuid import uuid4

from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from extratools_core.crudl import CRUDLDict
from extratools_core.json import JsonDict
from extratools_core.str import encode
from toolz.itertoolz import partition_all

from ..common.router import BaseRouter
from .helpers import (
    ClientErrorHandler,
    format_arn,
    get_client,
    get_service_resource,
)

default_service_resource: ServiceResource = get_service_resource("sqs")
__default_scheduler_client: BaseClient = get_client("scheduler")

type Queue = Any

FIFO_QUEUE_NAME_SUFFIX = ".fifo"


def get_queue_json(queue: Queue) -> JsonDict:
    return {
        "url": queue.url,
        "attributes": queue.attributes,
    }


def get_resource_dict(
    *,
    service_resource: ServiceResource | None = None,
    queue_name_prefix: str | None = None,
    json_only: bool = False,
) -> CRUDLDict[str, Queue | JsonDict]:
    service_resource = service_resource or default_service_resource

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/service-resource/index.html

    def check_queue_name(queue_name: str) -> None:
        if queue_name_prefix and not queue_name.startswith(queue_name_prefix):
            raise ValueError

    def create_func(queue_name: str | None, attributes: dict[str, str]) -> None:
        if queue_name is None:
            raise ValueError

        check_queue_name(queue_name)

        service_resource.create_queue(
            QueueName=queue_name,
            Attributes={
                **(
                    {
                        # Cannot specify `false` even for standard queue
                        "FifoQueue": "true",
                        # Scheduler requires it to be `true`
                        "ContentBasedDeduplication": "true",
                    } if queue_name.endswith(FIFO_QUEUE_NAME_SUFFIX)
                    else {}
                ),
                **attributes,
            },
        )

    @ClientErrorHandler(
        "QueueDoesNotExist",
        KeyError,
    )
    def read_func(queue_name: str) -> Queue:
        check_queue_name(queue_name)

        queue = service_resource.get_queue_by_name(
            QueueName=queue_name,
        )
        if not json_only:
            return queue

        return get_queue_json(queue)

    def update_func(queue_name: str, attributes: dict[str, str]) -> None:
        check_queue_name(queue_name)

        service_resource.get_queue_by_name(
            QueueName=queue_name,
        ).set_attributes(
            Attributes={
                **attributes,
            },
        )

    def delete_func(queue_name: str) -> None:
        check_queue_name(queue_name)

        service_resource.get_queue_by_name(
            QueueName=queue_name,
        ).delete()

    def list_func(_: None) -> Iterable[tuple[str, Queue]]:
        for queue in (
            service_resource.queues.filter(
                QueueNamePrefix=queue_name_prefix,
            )
            if queue_name_prefix
            else service_resource.queues.all()
        ):
            queue_name = cast("str", queue.url).rsplit('/', maxsplit=1)[-1]
            yield queue_name, (
                get_queue_json(queue) if json_only
                else queue
            )

    return CRUDLDict[str, Queue](
        create_func=create_func,
        read_func=read_func,
        update_func=update_func,
        delete_func=delete_func,
        list_func=list_func,
    )


MESSAGE_BATCH_SIZE = 10


def send_messages(
    queue: Queue,
    messages: Iterable[JsonDict],
    group: str | None = None,
    *,
    encoding: Literal["gzip", "zstd"] | None = None,
) -> Iterable[JsonDict]:
    batch_id = str(uuid4())

    fifo: bool = queue.url.endswith(FIFO_QUEUE_NAME_SUFFIX)
    if fifo and not group:
        raise ValueError

    for message_batch in partition_all(
        MESSAGE_BATCH_SIZE,
        (
            (f"{batch_id}_{i}", message_data)
            for i, message_data in enumerate(messages)
        ),
    ):
        response: JsonDict = queue.send_messages(Entries=[
            dict(
                Id=message_id,
                MessageBody=encode(
                    json.dumps(message_data),
                    encoding=encoding,
                ),
            ) | (
                dict(
                    MessageAttributes={
                        "ContentEncoding": {
                            "StringValue": encoding,
                            "DataType": "String",
                        },
                    },
                )
                if encoding else {}
            ) | (
                dict(
                    MessageGroupId=group,
                )
                if group else {}
            )
            for message_id, message_data in message_batch
        ])

        yield from response.get("Successful", [])
        yield from response.get("Failed", [])


def get_queue_arn(queue: Queue) -> str:
    return queue.attributes["QueueArn"]


def schedule_message(
    schedule: str,
    queue: Queue,
    message: JsonDict,
    group: str | None = None,
    *,
    scheduler_client: BaseClient | None = None,
    name_prefix: str = "extratools",
) -> str:
    # Length of 16 characters (from 8 bytes)
    random_id: str = token_hex(8)
    scheduler_name: str = f"{name_prefix}-{random_id}"

    (scheduler_client or __default_scheduler_client).create_schedule(
        GroupName=name_prefix,
        Name=scheduler_name,
        Target={
            "RoleArn": format_arn(
                "iam",
                "role",
                f"{name_prefix}-SchedulerExecution",
            ),
            "Arn": get_queue_arn(queue),
            # Note that encoding is not supported
            # as scheduler does not support specifying message attributes
            "Input": json.dumps(message),
            **(
                {
                    "SqsParameters": {
                        "MessageGroupId": group,
                    },
                } if group
                else {}
            ),
        },
        ScheduleExpression=schedule,
        FlexibleTimeWindow={
            "Mode": "OFF",
        },
    )
    return scheduler_name


class MessageGroupRouter(BaseRouter[str, str]):
    """
    Router utilizing groups
    - Each resource is queue base name (excluding specified prefix)
    - Each target is group name
      - Assuming each group name is unique across all queues in router
    - Each resource is also a target
      - Including existing ones
    """

    def __init__(
        self,
        *,
        service_resource: ServiceResource | None = None,
        queue_name_prefix: str,
        default_target_resource: str,
        encoding: Literal["gzip", "zstd"] | None = None,
    ) -> None:
        super().__init__(
            default_target_resource=default_target_resource,
        )

        self.__resource_dict: CRUDLDict[str, Queue] = get_resource_dict(
            service_resource=service_resource,
            queue_name_prefix=queue_name_prefix,
        )

        default_queue_name = queue_name_prefix + default_target_resource

        self.__queue_name_prefix = queue_name_prefix

        queue_name_prefix_len = len(queue_name_prefix)
        self.__queues: dict[str, Queue] = {
            default_target_resource: self.__resource_dict[default_queue_name],
        } | {
            queue_name[queue_name_prefix_len:]: queue
            for queue_name, queue in self.__resource_dict.items()
        }
        for resource in self.__queues:
            super().register_targets(resource, [resource])

        self.__encoding: Literal["gzip", "zstd"] | None = encoding

    @override
    def register_targets(
        self,
        resource: str,
        targets: Iterable[str],
        *,
        create: bool = True,
    ) -> None:
        super().register_targets(resource, targets)
        super().register_targets(resource, [resource])

        queue_name = self.__queue_name_prefix + resource

        if queue_name not in self.__resource_dict:
            if create:
                self.__resource_dict[queue_name] = {}
            else:
                raise KeyError

        self.__queues[resource] = self.__resource_dict[queue_name]

    @override
    def _route_to_resource(
        self,
        data: Iterable[JsonDict],
        resource: str,
        target: str,
    ) -> Iterable[JsonDict]:
        yield from send_messages(
            self.__queues[resource],
            data,
            target,
            encoding=self.__encoding,
        )


class FifoRouter(MessageGroupRouter):
    """
    Router utilizing FIFO queues and groups
    - Each resource is queue base name (excluding specified prefix and `.fifo` suffix)
    - Each target is group name
      - Assuming each group name is unique across all queues in router
    - Each resource is also a target
      - Including existing ones
    """

    def __init__(
        self,
        *,
        service_resource: ServiceResource | None = None,
        queue_name_prefix: str,
        default_target_resource: str,
        encoding: Literal["gzip", "zstd"] | None = None,
    ) -> None:
        super().__init__(
            service_resource=service_resource,
            queue_name_prefix=queue_name_prefix,
            default_target_resource=default_target_resource + ".fifo",
            encoding=encoding,
        )

    @override
    def register_targets(
        self,
        resource: str,
        targets: Iterable[str],
        *,
        create: bool = True,
    ) -> None:
        super().register_targets(resource + ".fifo", targets, create=create)
