import unittest

from lifeguard_rabbitmq.settings import (
    SETTINGS_MANAGER,
    get_rabbitmq_admin_instances,
)


class SettingsTest(unittest.TestCase):
    def test_lifeguard_rabbitmq_admin_base_url(self):
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_BASE_URL"][
                "default"
            ],
            "http://localhost:15672",
        )
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_BASE_URL"][
                "description"
            ],
            "RabbitMQ admin base url of default instance",
        )

    def test_lifeguard_rabbitmq_admin_user(self):
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_USER"]["default"],
            "guest",
        )
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_USER"][
                "description"
            ],
            "RabbitMQ admin user of default instance",
        )

    def test_lifeguard_rabbitmq_admin_passwd(self):
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_PASSWD"][
                "default"
            ],
            "guest",
        )
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_PASSWD"][
                "description"
            ],
            "RabbitMQ admin password of default instance",
        )

    def test_lifeguard_rabbitmq_admin_vhost(self):
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_VHOST"]["default"],
            "/",
        )
        self.assertEqual(
            SETTINGS_MANAGER.settings[r"LIFEGUARD_RABBITMQ_\w+_ADMIN_VHOST"][
                "description"
            ],
            "RabbitMQ admin virtual host of default instance",
        )

    def test_lifeguard_rabbitmq_admin_get_instances_attributes(self):
        default_instance = get_rabbitmq_admin_instances()["default"]

        self.assertEqual(default_instance["base_url"], "http://localhost:15672")
        self.assertEqual(default_instance["user"], "guest")
        self.assertEqual(default_instance["passwd"], "guest")
        self.assertEqual(default_instance["vhost"], "/")
