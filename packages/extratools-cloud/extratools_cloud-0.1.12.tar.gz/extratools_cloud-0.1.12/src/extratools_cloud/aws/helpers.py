import os
from collections.abc import Callable
from os import getenv
from typing import Any

import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

LOCAL_STAGE: str = "local"

STAGE: str = getenv("STAGE", LOCAL_STAGE)

LOCALSTACK_ENDPOINT: str = "http://localhost:4566"


def get_client(service: str, *, config: Config | None = None) -> BaseClient:
    return boto3.client(
        service,
        endpoint_url=(
            LOCALSTACK_ENDPOINT if STAGE == LOCAL_STAGE
            else None
        ),
        config=config,
    )


def get_service_resource(service: str) -> ServiceResource:
    return boto3.resource(
        service,
        endpoint_url=(
            LOCALSTACK_ENDPOINT if STAGE == LOCAL_STAGE
            else None
        ),
    )


class ClientErrorHandler:
    """
    Based on https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
    """

    def __init__(
        self,
        error_code: str,
        exception_class: type[Exception],
    ) -> None:
        self.__error_code = error_code
        self.__exception_class = exception_class

    def __call__(self, f: Callable[..., Any]) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except ClientError as e:
                error = e.response["Error"]
                # For SQS, somehow error code is found in
                # both `Code` and `QueryErrorCode` with different values
                # (`AWS.SimpleQueueService.NonExistentQueue` vs `QueueDoesNotExist`).
                # The value in `QueryErrorCode` seems to match public API doc.
                # https://github.com/aws/aws-sdk/issues/105
                if error.get("QueryErrorCode", error["Code"]) == self.__error_code:
                    raise self.__exception_class from e

                raise

        return wrapper


def get_account_id() -> str:
    return get_client("sts").get_caller_identity()["Account"]


def get_default_region() -> str | None:
    return os.getenv("AWS_DEFAULT_REGION")


def format_arn(
    service: str,
    resource_type: str | None,
    resource_id: str,
    *,
    account_id: str | None = None,
    region: str | None = None,
    resource_id_seperator: str = "/",
) -> str:
    """
    Based on https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html
    """

    resource: str = resource_id_seperator.join([
        resource_type,
        resource_id,
    ]) if resource_type else resource_id

    if service in {
        "account",
        "billing",
        "billingconductor",
        "budgets",
        "ce",
        "chatbot",
        "controlcatalog",
        "iam",
        "identitystore",
        "payments",
        "savingsplans",
        "sso",
        "sts",
    }:
        if region:
            raise ValueError

        region = ""
    else:
        region = get_default_region() if region is None else region

        # We do not know whether there are other services where region should be empty
        # Thus, we allow people passing empty string here
        if region is None:
            raise ValueError

    return ":".join([
        "arn",
        # Assuming `aws` partition right now
        "aws",
        service,
        region,
        account_id or get_account_id(),
        resource,
    ])
