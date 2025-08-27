import json
import logging
from typing import Any

from botocore.client import BaseClient
from botocore.config import Config
from extratools_core.func import Intercept
from extratools_core.json import JsonDict

from .helpers import get_client

logger = logging.getLogger(__name__)

# Lambda can run at most 15 minutes
MAX_FUNCTION_DURATION: int = 60 * 15

default_client: BaseClient = get_client(
    "lambda",
    # To prevent client timeout during long invocation
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/invoke.html
    config=Config(
        connect_timeout=MAX_FUNCTION_DURATION,
        read_timeout=MAX_FUNCTION_DURATION,
    ),
)


class InvocationError(RuntimeError):
    def __init__(self, message: str, error: JsonDict) -> None:
        self.message = message
        self.error = error


def invoke(
    function_name: str,
    payload: Any,
    *,
    client: BaseClient | None = None,
    wait: bool = True,
) -> Any:
    logger.info(
        f"Invoking Lambda function {function_name}"
        f" with payload:\n{json.dumps(payload)}",
    )

    response: JsonDict = (client or default_client).invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload).encode(),
        InvocationType=(
            "RequestResponse" if wait
            else "Event"
        ),
    )
    if not wait:
        return None

    response_payload: Any = json.load(response["Payload"])
    if func_error := response.get("FunctionError"):
        logger.error(
            f"Error during invocation of Lambda function {function_name}"
            f":\n{func_error}",
        )
        raise InvocationError(func_error, response_payload)

    return response_payload


class RequestResponseFunction(Intercept[JsonDict]):
    def __init__(
        self,
        function_name: str,
        *,
        client: BaseClient | None = None,
    ) -> None:
        def replacement(args: JsonDict) -> JsonDict:
            return invoke(function_name, args, client=client, wait=True)

        super().__init__(replacement)


class EventFunction(Intercept[None]):
    def __init__(
        self,
        function_name: str,
        *,
        client: BaseClient | None = None,
    ) -> None:
        def replacement(args: JsonDict) -> None:
            invoke(function_name, args, client=client, wait=False)

        super().__init__(replacement)
