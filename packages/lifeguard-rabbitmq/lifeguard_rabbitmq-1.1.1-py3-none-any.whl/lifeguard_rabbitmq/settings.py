"""
Lifeguard RabbitMQ Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        r"LIFEGUARD_RABBITMQ_\w+_ADMIN_BASE_URL": {
            "default": "http://localhost:15672",
            "description": "RabbitMQ admin base url of default instance",
        },
        r"LIFEGUARD_RABBITMQ_\w+_ADMIN_USER": {
            "default": "guest",
            "description": "RabbitMQ admin user of default instance",
        },
        r"LIFEGUARD_RABBITMQ_\w+_ADMIN_PASSWD": {
            "default": "guest",
            "description": "RabbitMQ admin password of default instance",
        },
        r"LIFEGUARD_RABBITMQ_\w+_ADMIN_VHOST": {
            "default": "/",
            "description": "RabbitMQ admin virtual host of default instance",
        },
        "LIFEGUARD_RABBITMQ_INSTANCES": {
            "default": "default",
            "description": "List of rabbitmq instances separated by comma",
        },
        "LIFEGUARD_RABBITMQ_USER": {
            "default": "guest",
            "description": "RabbitMQ user",
        },
        "LIFEGUARD_RABBITMQ_PASSWD": {
            "default": "guest",
            "description": "RabbitMQ password",
        },
        "LIFEGUARD_RABBITMQ_HOST": {
            "default": "localhost",
            "description": "RabbitMQ host",
        },
        "LIFEGUARD_RABBITMQ_VHOST": {
            "default": "/",
            "description": "RabbitMQ virtual host",
        },
    }
)

LIFEGUARD_RABBITMQ_INSTANCES = SETTINGS_MANAGER.read_value(
    "LIFEGUARD_RABBITMQ_INSTANCES"
).split(",")


def get_rabbitmq_admin_instances():
    """
    Recover attributes of each RabbitMQ Admin instances
    """
    instances = {}

    for instance in LIFEGUARD_RABBITMQ_INSTANCES:
        key = instance.upper()
        instances[instance] = {
            "base_url": SETTINGS_MANAGER.read_value(
                "LIFEGUARD_RABBITMQ_{}_ADMIN_BASE_URL".format(key)
            ),
            "user": SETTINGS_MANAGER.read_value(
                "LIFEGUARD_RABBITMQ_{}_ADMIN_USER".format(key)
            ),
            "passwd": SETTINGS_MANAGER.read_value(
                "LIFEGUARD_RABBITMQ_{}_ADMIN_PASSWD".format(key)
            ),
            "vhost": SETTINGS_MANAGER.read_value(
                "LIFEGUARD_RABBITMQ_{}_ADMIN_VHOST".format(key)
            ),
        }

    return instances
