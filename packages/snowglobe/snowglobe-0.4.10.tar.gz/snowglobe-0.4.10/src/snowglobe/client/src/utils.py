from logging import getLogger

import httpx

from .config import config, get_api_key_or_raise
from .models import SnowglobeData, SnowglobeMessage

LOGGER = getLogger(__name__)


async def fetch_experiments(app_id: str = None) -> list[dict]:
    """
    Fetch experiments from the Snowglobe server.

    Returns:
        list[dict]: A list of experiments.
    """
    async with httpx.AsyncClient() as client:
        experiments_url = f"{config.CONTROL_PLANE_URL}/api/experiments?&evaluated=false"
        if app_id:
            experiments_url += f"&appId={config.APPLICATION_ID}"
        experiments_response = await client.get(
            experiments_url,
            headers={"x-api-key": get_api_key_or_raise()},
        )

    if not experiments_response.status_code == 200:
        try:
            message = experiments_response.json().get("message")
        except Exception:
            message = experiments_response.text
        LOGGER.error(f"Error fetching experiments: {message}")
        raise Exception(
            f"{experiments_response.status_code} - {message or 'Unknown error'}"
        )
    experiments = experiments_response.json()
    return experiments


async def fetch_messages(*, test) -> list[SnowglobeMessage]:
    """
    Fetch messages from the Snowglobe server for a given test.

    Args:
        test (str): The test identifier.

    Returns:
        list[SnowglobeMessage]: A list of messages associated with the test.
    """
    # init messages
    messages = [
        SnowglobeMessage(
            role="user",
            content=test["prompt"],
            snowglobe_data=SnowglobeData(
                conversation_id=test["conversation_id"],
                test_id=test["id"],
            ),
        ),
    ]
    # if full turn append response
    if "response" in test and test["response"]:
        messages.append(
            SnowglobeMessage(
                role="assistant",
                content=test["response"],
                snowglobe_data=SnowglobeData(
                    conversation_id=test["conversation_id"],
                    test_id=test["id"],
                ),
            )
        )

    # build rest of messages
    parent_id = test.get("parent_test_id")
    async with httpx.AsyncClient() as client:
        while parent_id:
            # get parent test
            parent_test_response = await client.get(
                f"{config.CONTROL_PLANE_URL}/api/experiments/{test['experiment_id']}/tests/{parent_id}",
                headers={"x-api-key": get_api_key_or_raise()},
            )

            if not parent_test_response.status_code == 200:
                raise Exception(
                    f"Error fetching parent test {parent_id}: {parent_test_response.text}"
                )

            parent_test = parent_test_response.json()

            parent_id = parent_test.get("parent_test_id")

            messages.insert(
                0,
                SnowglobeMessage(
                    role="assistant",
                    content=parent_test["response"],
                    snowglobe_data=SnowglobeData(
                        conversation_id=parent_test["conversation_id"],
                        test_id=parent_test["id"],
                    ),
                ),
            )

            messages.insert(
                0,
                SnowglobeMessage(
                    role="user",
                    content=parent_test["prompt"],
                    snowglobe_data=SnowglobeData(
                        conversation_id=parent_test["conversation_id"],
                        test_id=parent_test["id"],
                    ),
                ),
            )

    return messages
