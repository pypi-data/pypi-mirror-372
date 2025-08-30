import os
from importlib.metadata import version as importlib_version
from typing import Callable
from functools import wraps

from snowglobe.client.src.models import CompletionRequest, RiskEvaluationRequest

try:
    import mlflow
    import mlflow.tracing
    from databricks.sdk import WorkspaceClient

    mlflow.tracing.enable()
except ImportError:
    mlflow = None

SNOWGLOBE_VERSION = importlib_version("snowglobe")


def trace_completion_fn(
    *,
    session_id: str,
    conversation_id: str,
    message_id: str,
    simulation_name: str,
    agent_name: str,
    span_type: str,
):
    def trace_decorator(completion_fn: Callable):
        disable_mlflow = os.getenv("SNOWGLOBE_DISABLE_MLFLOW_TRACING") or ""
        if mlflow and disable_mlflow.lower() != "true":
            w = WorkspaceClient()
            current_user = w.current_user.me()

            formatted_sim_name = simulation_name.lower().replace(" ", "_")
            default_experiment_name = f"/Users/{current_user.user_name}/{formatted_sim_name}"

            mlflow_experiment_name = (
                os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
            )
            mlflow.set_experiment(mlflow_experiment_name)

            mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
            if mlflow_active_model_id:
                mlflow.set_active_model(model_id=mlflow_active_model_id)
            else:
                mlflow.set_active_model(name=agent_name)

            span_attributes = {
                "snowglobe.version": SNOWGLOBE_VERSION,
                "type": span_type,
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "message_id": str(message_id),
                "simulation_name": simulation_name,
                "agent_name": agent_name,
            }

            @mlflow.trace(
                name=span_type,
                span_type=span_type,
                attributes=span_attributes,
            )
            @wraps(completion_fn)
            async def completion_fn_wrapper(test_request: CompletionRequest):
                try:
                    mlflow.update_current_trace(
                        metadata={"mlflow.trace.session": str(session_id)},
                        tags={
                            "session_id": str(session_id),
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "simulation_name": simulation_name,
                            "agent_name": agent_name,
                        },
                    )
                    response = await completion_fn(test_request)
                    return response
                except Exception as e:
                    raise e

            return completion_fn_wrapper
        else:
            return completion_fn

    return trace_decorator


def trace_risk_evaluation_fn(
    *,
    session_id: str,
    conversation_id: str,
    message_id: str,
    simulation_name: str,
    agent_name: str,
    span_type: str,
    risk_name,
):
    def trace_decorator(risk_evaluation_fn: Callable):
        disable_mlflow = os.getenv("SNOWGLOBE_DISABLE_MLFLOW_TRACING") or ""
        if mlflow and disable_mlflow.lower() != "true":
            w = WorkspaceClient()
            current_user = w.current_user.me()

            formatted_sim_name = simulation_name.lower().replace(" ", "_")
            default_experiment_name = f"/Users/{current_user.user_name}/{formatted_sim_name}"
        
            mlflow_experiment_name = (
                os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
            )
            mlflow.set_experiment(mlflow_experiment_name)

            mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
            if mlflow_active_model_id:
                mlflow.set_active_model(model_id=mlflow_active_model_id)
            else:
                mlflow.set_active_model(name=agent_name)

            span_attributes = {
                "snowglobe.version": SNOWGLOBE_VERSION,
                "type": span_type,
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "message_id": str(message_id),
                "simulation_name": simulation_name,
                "agent_name": agent_name,
                "risk_name": risk_name,
            }

            @mlflow.trace(
                name=span_type,
                span_type=span_type,
                attributes=span_attributes,
            )
            @wraps(risk_evaluation_fn)
            async def risk_evaluation_fn_wrapper(
                risk_evaluation_request: RiskEvaluationRequest,
            ):
                try:
                    mlflow.update_current_trace(
                        metadata={"mlflow.trace.session": str(session_id)},
                        tags={
                            "session_id": str(session_id),
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "simulation_name": simulation_name,
                            "agent_name": agent_name,
                            "risk_name": risk_name,
                        },
                    )
                    response = await risk_evaluation_fn(risk_evaluation_request)
                    return response
                except Exception as e:
                    raise e

            return risk_evaluation_fn_wrapper
        else:
            return risk_evaluation_fn

    return trace_decorator
