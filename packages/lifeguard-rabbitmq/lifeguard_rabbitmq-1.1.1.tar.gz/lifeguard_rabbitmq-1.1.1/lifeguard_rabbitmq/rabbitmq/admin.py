"""
RabbitMQ admin resources
"""
import json

from lifeguard.http_client import get

from lifeguard_rabbitmq.settings import get_rabbitmq_admin_instances

BASE_URL = "{}"
QUEUE = "/api/queues/{}/{}"


def count_consumers(instance_name, queue):
    """
    Get consumers for a queue
    """
    response = __queue_details(instance_name, queue)
    return len(response["consumer_details"])


def number_of_messages(instance_name, queue):
    """
    Get number of messages in queue
    """
    response = __queue_details(instance_name, queue)
    return response["messages"]


def __get(url, user, password):
    return json.loads(get(url, auth=(user, password)).content)


def __queue_details(instance_name, queue):
    instance_attributes = get_rabbitmq_admin_instances()[instance_name]
    url = __queue_url(QUEUE, instance_attributes, queue)
    return __get(url, instance_attributes["user"], instance_attributes["passwd"])


def __queue_url(api, instance_attributes, queue):
    return __url(api, instance_attributes["base_url"]).format(
        __vhost(instance_attributes["vhost"]), queue
    )


def __url(api, admin):
    return BASE_URL.format(admin) + api


def __vhost(vhost):
    return vhost.replace("/", "%2f")
