"""
RabbitMQ Plugin Endpoints
"""
from datetime import datetime
import json

from lifeguard.controllers import Response
from lifeguard_rabbitmq.context import RABBITMQ_PLUGIN_CONTEXT


def context_endpoint():
    """
    Endpoint to return plugin context
    """
    response = Response()
    response.content = json.dumps(RABBITMQ_PLUGIN_CONTEXT.get_attributes())
    response.status = 200
    response.content_type = "application/json"

    return response
