import unittest

from unittest.mock import patch

from lifeguard import NORMAL, PROBLEM
from lifeguard_rabbitmq.context import RABBITMQ_PLUGIN_CONTEXT
from lifeguard_rabbitmq.validations import (
    consumers_running_validation,
    messages_increasing_validation,
)


class ValidationTest(unittest.TestCase):
    def setUp(self):
        RABBITMQ_PLUGIN_CONTEXT.consumers_validation_options = {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {
                "rabbitmq_admin_instance": [
                    {"name": "queue_name", "min_number_of_consumers": 1}
                ]
            },
        }

        RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options = {
            "actions": [],
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
            "queues": {
                "rabbitmq_admin_instance": [
                    {"name": "queue_name", "count_before_alert": 10}
                ]
            },
        }

    @patch("lifeguard_rabbitmq.validations.count_consumers")
    def test_consumers_running_validation_when_normal(self, mock_count_consumers):
        mock_count_consumers.return_value = 1

        response = consumers_running_validation()

        self.assertEqual(response.status, NORMAL)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "queue": "queue_name",
                        "number_of_consumers": 1,
                        "status": "NORMAL",
                    }
                ]
            },
        )

    @patch("lifeguard_rabbitmq.validations.count_consumers")
    def test_consumers_running_validation_normal_with_more_than_min(
        self, mock_count_consumers
    ):
        mock_count_consumers.return_value = 2

        response = consumers_running_validation()

        self.assertEqual(response.status, NORMAL)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "queue": "queue_name",
                        "number_of_consumers": 2,
                        "status": "NORMAL",
                    }
                ]
            },
        )

    @patch("lifeguard_rabbitmq.validations.count_consumers")
    def test_consumers_running_validation_when_problem(self, mock_count_consumers):
        mock_count_consumers.return_value = 0

        response = consumers_running_validation()

        mock_count_consumers.assert_called_with("rabbitmq_admin_instance", "queue_name")
        self.assertEqual(response.validation_name, "consumers_running_validation")
        self.assertEqual(response.status, PROBLEM)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "queue": "queue_name",
                        "number_of_consumers": 0,
                        "status": "PROBLEM",
                    }
                ]
            },
        )

    @patch("lifeguard_rabbitmq.validations.count_consumers")
    @patch("lifeguard_rabbitmq.validations.logger")
    @patch("lifeguard_rabbitmq.validations.traceback")
    def test_consumers_running_validation_when_problem_because_integration_error(
        self, mock_traceback, mock_logger, mock_count_consumers
    ):
        mock_traceback.format_exc.return_value = "traceback"
        mock_count_consumers.side_effect = [Exception("error")]

        response = consumers_running_validation()

        mock_count_consumers.assert_called_with("rabbitmq_admin_instance", "queue_name")
        self.assertEqual(response.status, PROBLEM)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "error": "error on recover queue infos",
                        "queue": "queue_name",
                        "status": "PROBLEM",
                    }
                ]
            },
        )
        mock_logger.error.assert_called_with(
            "error on recover queue infos %s", "error", extra={"traceback": "traceback"}
        )

    @patch("lifeguard_rabbitmq.validations.number_of_messages")
    @patch("lifeguard_rabbitmq.validations.logger")
    def test_messages_increasing_validation_when_normal(
        self, mock_logger, mock_number_of_messages
    ):
        mock_number_of_messages.return_value = 0

        response = messages_increasing_validation()

        mock_number_of_messages.assert_called_with(
            "rabbitmq_admin_instance", "queue_name"
        )
        self.assertEqual(response.validation_name, "messages_increasing_validation")
        self.assertEqual(response.status, NORMAL)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "content": {
                            "counter": 0,
                            "number_of_messages": 0,
                            "status": "NORMAL",
                        },
                        "number_of_messages": 0,
                        "queue": "queue_name",
                        "status": "NORMAL",
                    }
                ]
            },
        )
        self.assertEqual(
            RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options,
            {
                "actions": [],
                "queues": {
                    "rabbitmq_admin_instance": [
                        {
                            "count_before_alert": 10,
                            "last_content": {
                                "counter": 0,
                                "number_of_messages": 0,
                                "status": "NORMAL",
                            },
                            "name": "queue_name",
                        }
                    ]
                },
                "schedule": {"every": {"minutes": 1}},
                "settings": {},
            },
        )

    @patch("lifeguard_rabbitmq.validations.number_of_messages")
    @patch("lifeguard_rabbitmq.validations.logger")
    def test_messages_increasing_validation_when_problem(
        self, mock_logger, mock_number_of_messages
    ):
        mock_number_of_messages.return_value = 10
        RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options = {
            "actions": [],
            "queues": {
                "rabbitmq_admin_instance": [
                    {
                        "count_before_alert": 10,
                        "last_content": {
                            "counter": 10,
                            "number_of_messages": 5,
                            "status": "NORMAL",
                        },
                        "name": "queue_name",
                    }
                ]
            },
            "schedule": {"every": {"minutes": 1}},
            "settings": {},
        }

        response = messages_increasing_validation()

        mock_number_of_messages.assert_called_with(
            "rabbitmq_admin_instance", "queue_name"
        )
        self.assertEqual(response.validation_name, "messages_increasing_validation")
        self.assertEqual(response.status, PROBLEM)
        self.assertEqual(
            response.details,
            {
                "rabbitmq_admin_instance": [
                    {
                        "content": {
                            "counter": 11,
                            "number_of_messages": 10,
                            "status": "PROBLEM",
                        },
                        "number_of_messages": 10,
                        "queue": "queue_name",
                        "status": "PROBLEM",
                    }
                ]
            },
        )
        self.assertEqual(
            RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options,
            {
                "actions": [],
                "queues": {
                    "rabbitmq_admin_instance": [
                        {
                            "count_before_alert": 10,
                            "last_content": {
                                "counter": 11,
                                "number_of_messages": 10,
                                "status": "PROBLEM",
                            },
                            "name": "queue_name",
                        }
                    ]
                },
                "schedule": {"every": {"minutes": 1}},
                "settings": {},
            },
        )
