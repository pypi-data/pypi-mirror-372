import unittest
from unittest.mock import patch

from lifeguard_rabbitmq.endpoints import context_endpoint


class EndpointsTest(unittest.TestCase):
    @patch("lifeguard_rabbitmq.endpoints.RABBITMQ_PLUGIN_CONTEXT")
    def test_context_endpoint(self, mock_context):
        mock_context.get_attributes.return_value = {}

        response = context_endpoint()

        self.assertEqual(response.content, "{}")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "application/json")
