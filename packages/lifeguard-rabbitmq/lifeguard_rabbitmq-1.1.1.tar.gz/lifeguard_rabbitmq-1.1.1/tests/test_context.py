import unittest

from lifeguard_rabbitmq.context import RabbitMQPluginContext


class ContextTest(unittest.TestCase):
    def setUp(self):
        def test_function():
            pass

        self.context = RabbitMQPluginContext()
        self.context.messages_increasing_validation_options = {
            "actions": [test_function],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {},
        }

    def test_serialize_context(self):

        self.assertEqual(
            self.context.get_attributes(),
            {
                "messages_increasing_validation_options": {
                    "actions": ["test_function"],
                    "schedule": {"every": {"minutes": 1}},
                    "settings": {},
                    "queues": {},
                },
                "consumers_validation_options": {
                    "actions": [],
                    "schedule": {"every": {"minutes": 1}},
                    "settings": {},
                    "queues": {},
                },
            },
        )
