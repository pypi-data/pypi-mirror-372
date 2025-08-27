import json
from collections.abc import Iterable

from botocore.client import BaseClient
from extratools_core.crudl import CRUDLDict
from extratools_core.json import JsonDict

from .helpers import ClientErrorHandler, get_client

default_client: BaseClient = get_client("cloudcontrol")


def get_resource_dict(
    resource_type: str,
    *,
    client: BaseClient | None = None,
) -> CRUDLDict[str, JsonDict]:
    client = client or default_client

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudcontrol.html

    @ClientErrorHandler(
        "ResourceNotFoundException",
        KeyError,
    )
    def read_func(identifier: str) -> JsonDict:
        return json.loads(client.get_resource(
            TypeName=resource_type,
            Identifier=identifier,
        )["ResourceDescription"]["Properties"])

    # Resource model may be treated as a special filter.
    # It must be specified for certain resource types,
    # yet must be unspecified for certain other resource types.
    # https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-operations-list.html#resource-operations-list-containers
    def list_func(resource_model: JsonDict | None) -> Iterable[tuple[str, JsonDict]]:
        paginator = client.get_paginator("list_resources")
        for page in paginator.paginate(
            TypeName=resource_type,
            **({} if resource_model is None else dict(
                ResourceModel=json.dumps(resource_model),
            )),
        ):
            for resource in page.get("ResourceDescriptions", []):
                yield (resource["Identifier"], json.loads(resource["Properties"]))

    return CRUDLDict[str, JsonDict](
        create_func=lambda _, desired_state: client.create_resource(
            TypeName=resource_type,
            DesiredState=json.dumps(desired_state),
        ),
        read_func=read_func,
        update_func=lambda identifier, patch: client.update_resource(
            TypeName=resource_type,
            Identifier=identifier,
            PatchDocument=json.dumps(patch),
        ),
        delete_func=lambda identifier: client.delete_resource(
            TypeName=resource_type,
            Identifier=identifier,
        ),
        list_func=list_func,
    )
