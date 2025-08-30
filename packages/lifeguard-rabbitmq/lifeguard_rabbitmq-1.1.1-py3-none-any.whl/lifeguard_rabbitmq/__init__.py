"""
Lifeguard integration with RabbitMQ
"""

from lifeguard.controllers import register_custom_controller
from lifeguard.validations import validation

from lifeguard_rabbitmq.context import RABBITMQ_PLUGIN_CONTEXT
from lifeguard_rabbitmq.endpoints import context_endpoint
from lifeguard_rabbitmq.validations import (
    consumers_running_validation,
    messages_increasing_validation,
)


def init(_lifeguard_context):
    register_custom_controller(
        "/lifeguard/rabbitmq/context", context_endpoint, {"methods": ["GET"]}
    )

    validation(
        "RabbitMQ Consumers Validation",
        RABBITMQ_PLUGIN_CONTEXT.consumers_validation_options["actions"],
        RABBITMQ_PLUGIN_CONTEXT.consumers_validation_options["schedule"],
        RABBITMQ_PLUGIN_CONTEXT.consumers_validation_options["settings"],
    )(consumers_running_validation)

    validation(
        "RabbitMQ Messages Increasing Validation",
        RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options["actions"],
        RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options["schedule"],
        RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options["settings"],
    )(messages_increasing_validation)
