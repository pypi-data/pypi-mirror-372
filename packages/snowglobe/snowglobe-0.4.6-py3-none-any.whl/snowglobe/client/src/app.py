# Set up the scheduler
import asyncio
import datetime
import importlib.util
import json
import logging
import os
import time
import traceback
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from functools import wraps
from logging import getLogger
from typing import Dict
from urllib.parse import quote_plus

import httpx
import uvicorn
from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, HTTPException, Request

from .cli_utils import info, shutdown_manager
from .config import config, get_api_key_or_raise
from .models import CompletionFunctionOutputs, CompletionRequest, RiskEvaluationRequest
from .stats import initialize_stats, track_batch_completion
from .utils import fetch_experiments, fetch_messages

# Configure logging - check DEBUG from environment directly to avoid config initialization
if os.getenv("DEBUG", "false").lower() == "true":
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=os.getenv("LOG_LEVEL", "DEBUG").upper(),
    )
else:
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
    )

LOGGER = getLogger("snowglobe_client")
# Allow LOG_LEVEL environment variable to override default INFO level
LOGGER.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()))

# In-memory storage for rate limiting per route
route_request_times = defaultdict(lambda: defaultdict(deque))


class ConfigurableRateLimiter:
    def __init__(self):
        self.route_configs = {}

    def configure_route(self, route_key: str, max_requests: int, time_window: int):
        """Configure rate limiting for a specific route"""
        self.route_configs[route_key] = {
            "max_requests": max_requests,
            "time_window": time_window,
        }

    def is_allowed(self, client_id: str, route_key: str) -> bool:
        # Get route configuration or use default
        config = self.route_configs.get(
            route_key, {"max_requests": 1, "time_window": 1}
        )
        max_requests = config["max_requests"]
        time_window = config["time_window"]

        now = time.time()
        client_requests = route_request_times[route_key][client_id]

        # Remove old requests outside the time window
        while client_requests and client_requests[0] <= now - time_window:
            client_requests.popleft()

        # Check if client has exceeded rate limit for this route
        if len(client_requests) >= max_requests:
            return False

        # Add current request time
        client_requests.append(now)
        return True

    def get_route_config(self, route_key: str) -> Dict[str, int]:
        """Get the configuration for a specific route"""
        return self.route_configs.get(route_key, {"max_requests": 1, "time_window": 1})


# Create global rate limiter instance
rate_limiter = ConfigurableRateLimiter()


def rate_limit(route_name: str, max_requests: int = 1, time_window: int = 1):
    """Decorator for per-route rate limiting with configurable limits"""

    def decorator(func):
        # Configure the route when decorator is applied
        rate_limiter.configure_route(route_name, max_requests, time_window)

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host

            if not rate_limiter.is_allowed(client_ip, route_name):
                config = rate_limiter.get_route_config(route_name)
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for route '{route_name}'. Maximum {config['max_requests']} requests per {config['time_window']} seconds.",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


queued_tests = {}
queued_evaluations = {}
risks = {}
apps = {}


async def process_application_heartbeat(app_id):
    connection_test_payload = {
        "appId": app_id,
    }
    try:
        prompt = "Hello from Snowglobe!"
        test_request = CompletionRequest(messages=[{"role": "user", "content": prompt}])
        completion_fn = apps.get(app_id, {}).get("completion_fn")
        if not completion_fn:
            LOGGER.warning(
                f"No completion function found for application {app_id}. Skipping heartbeat."
            )
            return
        if asyncio.iscoroutinefunction(completion_fn):
            response = await completion_fn(test_request)
        else:
            response = completion_fn(test_request)
        if not isinstance(response, CompletionFunctionOutputs):
            LOGGER.error(
                f"Completion function for application {app_id} did not return a valid response. Expected CompletionFunctionOutputs, got {type(response)}"
            )
            connection_test_payload["status"] = "failed"
            connection_test_payload["error"] = (
                "Completion function did not return a valid response. "
                "Expected CompletionFunctionOutputs, got {type(response)}"
            )

        if not hasattr(response, "response") or not isinstance(response.response, str):
            LOGGER.error(
                f"Completion function for application {app_id} did not return a valid response. Expected a string, got {type(response.response)}"
            )
            connection_test_payload["status"] = "failed"
            connection_test_payload[
                "error"
            ] = "Completion function did not return a valid response. Expected a string, got {type(response.response)}"

        if response.response == "This is a string response from your application":
            LOGGER.error(
                f"Completion function for application {app_id} returned a default response. This indicates the application is not properly connected."
            )
            connection_test_payload["status"] = "failed"
            connection_test_payload[
                "error"
            ] = "Completion function returned a default response. "

        if connection_test_payload.get("status") != "failed":
            connection_test_payload["response"] = response.response
            connection_test_payload["prompt"] = prompt

    except Exception as e:
        connection_test_payload["status"] = "failed"
        connection_test_payload["error"] = f"{str(e)}\n{traceback.format_exc()}"
        connection_test_payload["app_id"] = app_id
        connection_test_payload["applicationId"] = app_id

    connection_test_url = (
        f"{config.CONTROL_PLANE_URL}/api/successful-code-connection-tests"
    )

    if connection_test_payload.get("status") == "failed":
        connection_test_url = (
            f"{config.CONTROL_PLANE_URL}/api/failed-code-connection-tests"
        )

    async with httpx.AsyncClient() as client:
        LOGGER.info(
            f"Posting code connection test for application {app_id} connection_test_payload: {connection_test_payload}"
        )
        connection_test_response = await client.post(
            connection_test_url,
            json=connection_test_payload,
            headers={"x-api-key": get_api_key_or_raise()},
        )

    if not connection_test_response.is_success:
        LOGGER.error(
            f"Error posting code connection test for application {app_id}: {connection_test_response.text}"
        )
    return connection_test_response.json()


async def process_risk_evaluation(test, risk_name):
    """finds correct risk and calls the risk evaluation function and creates a risk evaluation for the test"""
    start = time.time()

    messages = await fetch_messages(test=test)

    if asyncio.iscoroutinefunction(risks[risk_name]):
        risk_evaluation = await risks[risk_name](
            RiskEvaluationRequest(messages=messages)
        )
    else:
        risk_evaluation = risks[risk_name](RiskEvaluationRequest(messages=messages))

    LOGGER.debug(f"Risk evaluation output: {risk_evaluation}")

    # Extract fields from risk_evaluation object
    severity = getattr(risk_evaluation, "severity", "")
    reason = getattr(risk_evaluation, "reason", "")
    risk_triggered = getattr(risk_evaluation, "triggered", "")

    response_xml = (
        f"<risk>"
        f"<name>{risk_name}</name>"
        f"<severity>{severity}</severity>"
        f"<reason>{reason}</reason>"
        f"<risk_triggered>{risk_triggered}</risk_triggered>"
        f"</risk>"
    )

    # Post a Risk Evaluation (async)
    async with httpx.AsyncClient() as client:
        risk_evaluation_response = await client.post(
            f"{config.CONTROL_PLANE_URL}/api/experiments/{test['experiment_id']}/tests/{test['id']}/evaluations",
            json={
                "test_id": test["id"],
                "judge_prompt": "",  # does this need to be set?
                "judge_response": response_xml,
                "risk_type": risk_name,
                "risk_triggered": risk_evaluation.triggered,
            },
            headers={"x-api-key": get_api_key_or_raise()},
        )
    LOGGER.debug(f"Time taken: {time.time() - start} seconds")
    if not risk_evaluation_response.is_success:
        LOGGER.error("Error posting risk evaluation", risk_evaluation_response.text)
        raise Exception("Error posting risk evaluation, task is not healthy")


async def process_test(test, completion_fn, app_id):
    """Processes a test by converting it to OpenAI style messages and calling the completion function"""
    start = time.time()
    # convert test to openai style messages
    messages = await fetch_messages(test=test)

    if asyncio.iscoroutinefunction(completion_fn):
        completionOutput = await completion_fn(CompletionRequest(messages=messages))
    else:
        completionOutput = completion_fn(CompletionRequest(messages=messages))

    LOGGER.debug(f"Completion output: {completionOutput}")

    async with httpx.AsyncClient() as client:
        await client.put(
            f"{config.CONTROL_PLANE_URL}/api/experiments/{test['experiment_id']}/tests/{test['id']}",
            json={
                "id": test["id"],
                "appId": app_id,
                "prompt": test["prompt"],
                "response": completionOutput.response,
                "persona": test["persona"],
            },
            headers={"x-api-key": get_api_key_or_raise()},
        )
    LOGGER.debug(f"Time taken: {time.time() - start} seconds")
    # remove test['id'] from queued_tests
    queued_tests.pop(test["id"], None)

    return completionOutput


# The task to run
async def poll_for_completions():
    # Exit early if shutdown requested
    if await shutdown_manager.is_async_shutdown_requested():
        return

    job_id = "poll_for_completions"

    if len(apps) == 0:
        LOGGER.warning("No applications found. Skipping completions check.")
        return

    # Register this job as active
    shutdown_manager.register_active_job(job_id)

    try:
        experiments = await fetch_experiments()
    except Exception as e:
        # Handle shutdown-related connection errors gracefully
        if shutdown_manager.is_shutdown_requested():
            LOGGER.debug(f"Connection error during shutdown (expected): {e}")
            return
        else:
            LOGGER.error(f"Error fetching experiments: {e}")
            raise
    finally:
        shutdown_manager.unregister_active_job(job_id)

    try:
        async with httpx.AsyncClient() as client:
            LOGGER.info(f"Polling {len(experiments)} experiments for completions...")
            for experiment in experiments:
                LOGGER.debug(
                    f"Checking experiment: id={experiment.get('id')}, name={experiment.get('name', 'unknown')}"
                )

            for experiment in experiments:
                # Check for shutdown between each experiment
                if await shutdown_manager.is_async_shutdown_requested():
                    LOGGER.debug("Shutdown requested, stopping completions polling")
                    return

                app_id = experiment.get("app_id")
                if app_id not in apps:
                    LOGGER.debug(
                        f"Skipping experiment as we do not have a completion function for app_id: {app_id}"
                    )
                    continue
                experiment_id = experiment["id"]

                try:
                    experiment_request = await client.get(
                        f"{config.CONTROL_PLANE_URL}/api/experiments/{experiment_id}?appId={app_id}",
                        headers={"x-api-key": get_api_key_or_raise()},
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if shutdown_manager.is_shutdown_requested():
                        LOGGER.debug(f"HTTP error during shutdown (expected): {e}")
                        return
                    else:
                        LOGGER.error(
                            f"Connection error fetching experiment {experiment_id}: {e}"
                        )
                        continue

                if not experiment_request.is_success:
                    LOGGER.error(
                        f"Error fetching experiment {experiment_id}: {experiment_request.text}"
                    )
                    continue
                experiment = experiment_request.json()

                limit = 10
                LOGGER.debug(f"Checking for tests for experiment {experiment_id}")

                try:
                    tests_response = await client.get(
                        f"{config.CONTROL_PLANE_URL}/api/experiments/{experiment_id}/tests?appId={app_id}&include-risk-evaluations=false&limit={limit}&unprocessed-only=true",
                        headers={"x-api-key": get_api_key_or_raise()},
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if shutdown_manager.is_shutdown_requested():
                        LOGGER.debug(f"HTTP error during shutdown (expected): {e}")
                        return
                    else:
                        LOGGER.error(f"Connection error fetching tests: {e}")
                        continue

                if not tests_response.is_success:
                    LOGGER.error(f"Error fetching tests: {tests_response.text}")
                    continue

                tests = tests_response.json()
                completion_count = 0
                for test in tests:
                    # Check for shutdown before processing each test
                    if await shutdown_manager.is_async_shutdown_requested():
                        LOGGER.debug("Shutdown requested, stopping test processing")
                        return

                    LOGGER.debug(
                        f"Found test {test['id']} for experiment {experiment_id}"
                    )
                    if not test["response"] and test["id"] not in queued_tests:
                        try:
                            completion_request = await httpx.AsyncClient().post(
                                f"{config.SNOWGLOBE_CLIENT_URL}/completion",
                                json={"test": test, "app_id": app_id},
                                timeout=30,
                            )
                        except (httpx.ConnectError, httpx.TimeoutException) as e:
                            if shutdown_manager.is_shutdown_requested():
                                LOGGER.debug(
                                    f"HTTP error during shutdown (expected): {e}"
                                )
                                return
                            else:
                                LOGGER.error(
                                    f"Connection error posting completion: {e}"
                                )
                                continue

                        # if 429 raise and exception and stop this batch
                        if (
                            not completion_request.is_success
                            and completion_request.status_code == 429
                        ):
                            LOGGER.warning(
                                f"Completion Rate limit exceeded for test {test['id']}: {completion_request.text}"
                            )
                            raise ValueError(
                                status_code=429,
                                detail=f"Rate limit exceeded for test {test['id']}",
                            )
                        completion_count += 1
                        queued_tests[test["id"]] = True

                if completion_count > 0:
                    experiment_name = experiment.get("name", "unknown")
                    if LOGGER.level <= logging.INFO:  # Verbose mode
                        LOGGER.info(
                            f"Processed {completion_count} completions for experiment {experiment_name} ({experiment_id})"
                        )
                    else:  # Clean UI mode
                        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                        info(
                            f"[{timestamp}] ✓ Batch complete: {completion_count} responses sent ({experiment_name})"
                        )

                        # Track batch completion
                        track_batch_completion(experiment_name, completion_count)

    except Exception as e:
        # Handle any other errors
        if shutdown_manager.is_shutdown_requested():
            LOGGER.debug(f"Error during shutdown (expected): {e}")
        else:
            LOGGER.error(f"Unexpected error in poll_for_completions: {e}")
            raise


async def process_application_heartbeats():
    # Exit early if shutdown requested
    if await shutdown_manager.is_async_shutdown_requested():
        return

    job_id = "process_application_heartbeats"
    shutdown_manager.register_active_job(job_id)

    try:
        connection_test_count = 0
        LOGGER.info("Processing application heartbeats...")
        for app_id, app_info in apps.items():
            # Check for shutdown between each heartbeat
            if await shutdown_manager.is_async_shutdown_requested():
                LOGGER.debug("Shutdown requested, stopping heartbeats")
                return

            try:
                connection_test_request = await httpx.AsyncClient().post(
                    f"{config.SNOWGLOBE_CLIENT_URL}/heartbeat",
                    json={"app_id": app_id},
                    timeout=30,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if shutdown_manager.is_shutdown_requested():
                    LOGGER.debug(f"HTTP error during shutdown (expected): {e}")
                    return
                else:
                    LOGGER.error(
                        f"Connection error sending heartbeat for {app_id}: {e}"
                    )
                    continue

            if not connection_test_request.is_success:
                LOGGER.error(
                    f"Error sending heartbeat for application {app_id}: {connection_test_request.text}"
                )
                continue
            connection_test_count += 1

        LOGGER.info(f"Processed {connection_test_count} heartbeats for applications.")
    finally:
        shutdown_manager.unregister_active_job(job_id)


async def poll_for_risk_evaluations():
    """Poll for risk evaluations and process them."""
    # Exit early if shutdown requested
    if await shutdown_manager.is_async_shutdown_requested():
        return

    job_id = "poll_for_risk_evaluations"
    shutdown_manager.register_active_job(job_id)

    try:
        experiments = await fetch_experiments()
    except Exception as e:
        # Handle shutdown-related connection errors gracefully
        if shutdown_manager.is_shutdown_requested():
            LOGGER.debug(f"Connection error during shutdown (expected): {e}")
            return
        else:
            LOGGER.error(f"Error fetching experiments: {e}")
            raise
    finally:
        shutdown_manager.unregister_active_job(job_id)

    try:
        LOGGER.info("Checking for pending risk evaluations...")
        LOGGER.debug(
            f"Found {len(experiments)} experiments with validation in progress"
        )

        async with httpx.AsyncClient() as client:
            for experiment in experiments:
                # Check for shutdown between experiments
                if await shutdown_manager.is_async_shutdown_requested():
                    LOGGER.debug("Shutdown requested, stopping risk evaluations")
                    return

                try:
                    experiment_request = await client.get(
                        f"{config.CONTROL_PLANE_URL}/api/experiments/{experiment['id']}",
                        headers={"x-api-key": get_api_key_or_raise()},
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if shutdown_manager.is_shutdown_requested():
                        LOGGER.debug(f"HTTP error during shutdown (expected): {e}")
                        return
                    else:
                        LOGGER.error(
                            f"Connection error fetching experiment {experiment['id']}: {e}"
                        )
                        continue

                if not experiment_request.is_success:
                    LOGGER.error(
                        f"Error fetching experiment {experiment['id']}: {experiment_request.text}"
                    )
                    continue
                experiment = experiment_request.json()
                risk_eval_count = 0

                for risk_name in risks.keys():
                    # Check for shutdown before processing each risk
                    if await shutdown_manager.is_async_shutdown_requested():
                        LOGGER.debug("Shutdown requested, stopping risk processing")
                        return

                    try:
                        if (
                            risk_name
                            not in experiment.get("source_data", {})
                            .get("evaluation_configuration", {})
                            .keys()
                        ):
                            LOGGER.debug(
                                f"Skipping experiment {experiment['id']} as it does not have risk {risk_name}"
                            )
                            continue
                        LOGGER.debug(
                            f"checking for tests for experiment {experiment['id']}"
                        )

                        try:
                            tests_response = await client.get(
                                f"{config.CONTROL_PLANE_URL}/api/experiments/{experiment['id']}/tests?unevaluated-risk={quote_plus(risk_name)}&include-risk-evaluations=true",
                                headers={"x-api-key": get_api_key_or_raise()},
                            )
                        except (httpx.ConnectError, httpx.TimeoutException) as e:
                            if shutdown_manager.is_shutdown_requested():
                                LOGGER.debug(
                                    f"HTTP error during shutdown (expected): {e}"
                                )
                                return
                            else:
                                LOGGER.error(f"Connection error fetching tests: {e}")
                                continue

                        if not tests_response.is_success:
                            message = (
                                tests_response.json().get("message")
                                or tests_response.text
                            )
                            raise ValueError(
                                status_code=tests_response.status_code,
                                message=message,
                            )
                        tests = tests_response.json()

                        for test in tests:
                            # Check for shutdown before processing each test
                            if await shutdown_manager.is_async_shutdown_requested():
                                LOGGER.debug(
                                    "Shutdown requested, stopping test evaluation"
                                )
                                return

                            test_id = test["id"]
                            if (
                                test_id not in queued_evaluations
                                and test.get("response") is not None
                            ):
                                try:
                                    risk_eval_response = await httpx.AsyncClient().post(
                                        f"{config.SNOWGLOBE_CLIENT_URL}/risk-evaluation",
                                        json={"test": test, "risk_name": risk_name},
                                        timeout=30,
                                    )
                                except (
                                    httpx.ConnectError,
                                    httpx.TimeoutException,
                                ) as e:
                                    if shutdown_manager.is_shutdown_requested():
                                        LOGGER.debug(
                                            f"HTTP error during shutdown (expected): {e}"
                                        )
                                        return
                                    else:
                                        LOGGER.error(
                                            f"Connection error posting risk evaluation: {e}"
                                        )
                                        continue

                                # if risk evaltion response is 429 raise and exception and bail on this batch
                                if (
                                    not risk_eval_response.is_success
                                    and risk_eval_response.status_code == 429
                                ):
                                    LOGGER.error(
                                        f"Rate limit exceeded for risk evaluation {test['id']}: {risk_eval_response.text}"
                                    )
                                    raise ValueError(
                                        status_code=429,
                                        detail=f"Rate limit exceeded for risk evaluation {test['id']}",
                                    )
                                queued_evaluations[test_id] = True
                                risk_eval_count += 1
                    except Exception as e:
                        if shutdown_manager.is_shutdown_requested():
                            LOGGER.debug(f"Error during shutdown (expected): {e}")
                            return
                        else:
                            LOGGER.error(f"Error fetching tests: {e}")

                if risk_eval_count > 0:
                    LOGGER.info(
                        f"Processed {risk_eval_count} risk evaluations for experiment {experiment.get('name', 'unknown')} ({experiment['id']})"
                    )

    except Exception as e:
        # Handle any other errors
        if shutdown_manager.is_shutdown_requested():
            LOGGER.debug(f"Error during shutdown (expected): {e}")
        else:
            LOGGER.error(f"Unexpected error in poll_for_risk_evaluations: {e}")
            raise


# Ensure the scheduler shuts down properly on application exit.
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Load agents from .snowglobe/agents.json system
        agents_json_path = os.path.join(os.getcwd(), ".snowglobe", "agents.json")
        if os.path.exists(agents_json_path):
            try:
                with open(agents_json_path, "r") as f:
                    agents_data = json.load(f)

                for filename, agent_info in agents_data.items():
                    try:
                        app_id = agent_info["uuid"]
                        app_name = agent_info["name"]
                        agent_file_path = os.path.join(os.getcwd(), filename)

                        if not os.path.exists(agent_file_path):
                            LOGGER.warning(f"Agent file not found: {agent_file_path}")
                            continue

                        spec = importlib.util.spec_from_file_location(
                            "agent_wrapper", agent_file_path
                        )
                        agent_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(agent_module)

                        if not hasattr(agent_module, "process_scenario"):
                            LOGGER.warning(
                                f"Agent {filename} does not have a process_scenario function"
                            )
                            continue

                        apps[app_id] = {
                            "completion_fn": agent_module.process_scenario,
                            "name": app_name,
                        }

                    except Exception as e:
                        LOGGER.error(f"Error loading agent {filename}: {e}")
                        continue

            except (json.JSONDecodeError, IOError) as e:
                LOGGER.error(f"Error reading agents.json: {e}")
        else:
            LOGGER.warning(
                "No .snowglobe/agents.json found. Run 'snowglobe-connect init' to set up an agent."
            )

        for app_id, app_info in apps.items():
            LOGGER.info(
                f"Loaded application {app_info['name']} with ID {app_id} for completions."
            )
        if config.APPLICATION_ID:
            if config.APPLICATION_ID not in apps:
                LOGGER.warning(
                    "\n********* START WARNING *********"
                    f"\nLegacy single application detected with ID {config.APPLICATION_ID}. "
                    "\nPlease migrate to the new applications structure."
                    f"\nRun snowglobe-connect init and follow the prompts to set up your application."
                    "\nThis configuration option will be removed in the next major release."
                    "\n********* END WARNING *********"
                )
                # load the legacy applications connect file out of the base of this directory
                legacy_connect_file = os.path.join(os.getcwd(), "snowglobe_connect.py")
                if os.path.exists(legacy_connect_file):
                    spec = importlib.util.spec_from_file_location(
                        "snowglobe_connect", legacy_connect_file
                    )
                    sg_connect = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(sg_connect)
                    if hasattr(sg_connect, "completion_fn"):
                        apps[config.APPLICATION_ID] = {
                            "completion_fn": sg_connect.completion_fn,
                            "name": "Legacy Single Application",
                        }
                        LOGGER.info(
                            f"Loaded legacy application with ID {config.APPLICATION_ID} for completions."
                        )
                    else:
                        LOGGER.error(
                            f"Legacy application with ID {config.APPLICATION_ID} does not have a completion_fn."
                        )
    except Exception as e:
        LOGGER.error(f"Error loading applications: {e}")

    # attempt to judge risks from custom_risks/
    # each judge name is encoded in the filename with spaces replaced by underscores
    try:
        risks_dir = os.path.join(os.getcwd(), "custom_risks")
        if os.path.exists(risks_dir):
            for judge_file in os.listdir(risks_dir):
                if judge_file.endswith(".py"):
                    judge_name = judge_file[:-3].replace("_", " ")

                    spec = importlib.util.spec_from_file_location(
                        judge_name, os.path.join(risks_dir, judge_file)
                    )
                    judge_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(judge_module)
                    if hasattr(judge_module, "risk_evaluation_fn"):
                        risks[judge_name] = judge_module.risk_evaluation_fn
                    else:
                        LOGGER.warning(
                            f"Judge {judge_name} does not have a risk_evaluation_fn. Skipping."
                        )
        LOGGER.info(f"Loaded risks: {list(risks.keys())}")
    except Exception as e:
        LOGGER.error(
            f"Error loading risks from custom_risks: {e}. Custom judging will not be available."
        )

    async with AsyncScheduler() as scheduler:
        await scheduler.add_schedule(poll_for_completions, IntervalTrigger(seconds=3))
        await scheduler.add_schedule(
            poll_for_risk_evaluations, IntervalTrigger(seconds=7)
        )
        await scheduler.add_schedule(
            process_application_heartbeats, IntervalTrigger(minutes=5)
        )
        await scheduler.start_in_background()
        yield
    # try to loop over applications and send a failed connection test
    for app_id in apps.keys():
        try:
            connection_test_url = (
                f"{config.CONTROL_PLANE_URL}/api/failed-code-connection-tests"
            )
            connection_test_payload = {
                "appId": app_id,
                "status": "failed",
                "error": "snowglobe-connect shut down gracefully",
            }
            async with httpx.AsyncClient() as client:
                LOGGER.info(
                    f"Posting shut down code connection test for application {app_id} connection_test_payload: {connection_test_payload}"
                )
                connection_test_response = await client.post(
                    connection_test_url,
                    json=connection_test_payload,
                    headers={"x-api-key": config.API_KEY},
                )
            if not connection_test_response.is_success:
                LOGGER.error(
                    f"Error posting shut down code connection test for application {app_id}: {connection_test_response.text}"
                )
            LOGGER.info(
                f"Posted shut down heart beat for application {app_id} successfully."
            )
        except Exception as e:
            LOGGER.error(
                f"Error processing application heartbeat for {app_id}: {e}\n{traceback.format_exc()}"
            )
    await scheduler.stop()
    await scheduler.wait_until_stopped()


def create_client():
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=lifespan)

    @app.get("/")
    def read_root():
        return {"message": "Dashing through the snow..."}

    @app.post("/completion")
    @rate_limit(
        "completion",
        max_requests=config.CONCURRENT_COMPLETIONS_PER_INTERVAL,
        time_window=config.CONCURRENT_COMPLETIONS_INTERVAL_SECONDS,
    )
    async def completion_endpoint(request: Request):
        # request body is test
        completion_body = await request.json()
        test = completion_body.get("test")
        app_id = completion_body.get("app_id")
        # both are required non empty strings
        if not test or not app_id:
            raise HTTPException(
                status_code=400,
                detail="Both 'test' and 'app_id' must be provided in the request body.",
            )
        if app_id not in apps:
            raise HTTPException(
                status_code=404,
                detail=f"Application with ID {app_id} not found.",
            )
        completion_fn = apps.get(app_id, {}).get("completion_fn")
        LOGGER.debug(f"Received test: {test['id']}")

        await process_test(test, completion_fn, app_id)
        return {"status": "processed"}

    @app.post("/heartbeat")
    @rate_limit(
        "heartbeat",
        max_requests=config.CONCURRENT_HEARTBEATS_PER_INTERVAL,
        time_window=config.CONCURRENT_HEARTBEATS_INTERVAL_SECONDS,
    )
    async def heartbeat_endpoint(request: Request):
        """Endpoint to check if the client is alive and well."""
        body = await request.json()
        app_id = body.get("app_id")
        if not app_id:
            raise HTTPException(
                status_code=400,
                detail="Application ID must be provided in the request body.",
            )
        if app_id not in apps:
            raise HTTPException(
                status_code=404,
                detail=f"Application with ID {app_id} not found.",
            )
        LOGGER.debug(f"Received heartbeat for application: {app_id}")

        # Simulate processing heartbeat
        await process_application_heartbeat(app_id)
        return {"status": "heartbeat received"}

    @app.post("/risk-evaluation")
    @rate_limit(
        "risk_evaluation",
        max_requests=config.CONCURRENT_RISK_EVALUATIONS,
        time_window=config.CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS,
    )
    async def risk_evaluation_endpoint(request: Request):
        # request body is test
        body = await request.json()
        test = body.get("test")
        risk_name = body.get("risk_name")
        LOGGER.debug(f"Received risk evaluation for test: {test['id']}")

        # For now, just simulate processing
        await process_risk_evaluation(test, risk_name)
        return {"status": "risk evaluation processed"}

    return app


def start_client(verbose=False):
    """Start the FastAPI client."""
    # Configure logging based on verbose flag
    if not verbose:
        LOGGER.setLevel(logging.WARNING)
        logging.getLogger("apscheduler").setLevel(logging.ERROR)

    # Initialize stats tracking
    initialize_stats()

    app = create_client()

    port = config.SNOWGLOBE_CLIENT_PORT
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


if __name__ == "__main__":
    start_client()
