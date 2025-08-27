"""
RabbitMQ Plugin Context
"""


class RabbitMQPluginContext:
    """
    RabbitMQ Context
    """

    def __init__(self):
        self._consumers_validation_options = {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {},
        }

        self._messages_increasing_validation_options = {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {},
        }

    @property
    def consumers_validation_options(self):
        """
        Getter for consumers validation options
        """
        return self._consumers_validation_options

    @consumers_validation_options.setter
    def consumers_validation_options(self, value):
        """
        Setter for consumers validation options

        Example:

        {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {
                "rabbitmq_admin_instance": [{"name": "queue_name", "min_number_of_consumers": 1}]
            }
        }
        """
        self._consumers_validation_options = value

    @property
    def messages_increasing_validation_options(self):
        """
        Getter for messages increasing validation options
        """
        return self._messages_increasing_validation_options

    @messages_increasing_validation_options.setter
    def messages_increasing_validation_options(self, value):
        """
        Setter for messages increasing validation options

        Example:

        {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {
                "rabbitmq_admin_instance": [{"name": "queue_name", "count_before_alert": 10}]
            }
        }
        """
        self._messages_increasing_validation_options = value

    def get_attributes(self):
        """
        Return all attributes in a dict.
        """
        return {
            "messages_increasing_validation_options": serialize_options(
                self.messages_increasing_validation_options
            ),
            "consumers_validation_options": serialize_options(
                self.consumers_validation_options
            ),
        }


def serialize_options(options):
    cloned_options = options.copy()
    cloned_options["actions"] = [
        action.__name__ for action in cloned_options["actions"]
    ]
    return cloned_options


RABBITMQ_PLUGIN_CONTEXT = RabbitMQPluginContext()
