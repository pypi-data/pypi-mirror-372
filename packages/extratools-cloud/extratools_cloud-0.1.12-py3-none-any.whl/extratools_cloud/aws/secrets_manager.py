import json
from collections.abc import Iterable
from typing import Literal

from botocore.client import BaseClient
from extratools_core.crudl import CRUDLDict
from extratools_core.json import JsonDict
from extratools_core.str import decode, encode

from .helpers import ClientErrorHandler, get_client

default_client: BaseClient = get_client("secretsmanager")


def get_resource_dict(
    *,
    secret_name_prefix: str | None = None,
    client: BaseClient | None = None,
    encoding: Literal["gzip", "zstd"] | None = None,
    force_delete: bool = False,
) -> CRUDLDict[str, JsonDict]:
    client = client or default_client

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html

    def check_secret_name(secret_name: str) -> str:
        if secret_name_prefix and not secret_name.startswith(secret_name_prefix):
            raise ValueError

        return secret_name

    def create_func(secret_name: str | None, value: JsonDict) -> None:
        if secret_name is None:
            raise ValueError

        client.create_secret(
            Name=check_secret_name(secret_name),
            # It is possible to use `SecretBinary` to store compressed binary directly
            # without further Base64 encoding to store compressed string with 33%+ size overhead.
            # https://en.wikipedia.org/wiki/Base64
            # However, it would also make code more complex.
            SecretString=encode(json.dumps(value), encoding=encoding),
        )

    @ClientErrorHandler(
        "ResourceNotFoundException",
        KeyError,
    )
    def read_func(secret_name: str) -> JsonDict:
        return json.loads(decode(
            client.get_secret_value(
                SecretId=check_secret_name(secret_name),
            )["SecretString"],
            encoding=encoding,
        ))

    def list_func(_: None) -> Iterable[tuple[str, None]]:
        paginator = client.get_paginator("list_secrets")
        for page in paginator.paginate(
            **({} if secret_name_prefix is None else dict(
                Filters=[{
                    "Key": "name",
                    "Values": [secret_name_prefix],
                }],
            )),
        ):
            for secret in page.get("SecretList", []):
                # It seems LocalStack always return delete secret even if
                # `IncludePlannedDeletion` is set to false.
                if "DeletedDate" not in secret:
                    yield (secret["Name"], None)

    return CRUDLDict[str, JsonDict](
        create_func=create_func,
        read_func=read_func,
        update_func=lambda secret_name, value: client.put_secret_value(
            SecretId=check_secret_name(secret_name),
            SecretString=encode(json.dumps(value), encoding=encoding),
        ),
        delete_func=lambda secret_name: client.delete_secret(
            SecretId=check_secret_name(secret_name),
            ForceDeleteWithoutRecovery=force_delete,
        ),
        list_func=list_func,
    )
