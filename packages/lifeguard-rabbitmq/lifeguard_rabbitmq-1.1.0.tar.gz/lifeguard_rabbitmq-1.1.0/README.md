# Lifeguard RabbitMQ

## Usage

Configure plugin in `lifeguard_settings.py`.

```python
import lifeguard_rabbitmq

PLUGINS = [lifeguard_rabbitmq]
```

## Settings

Name                                       | Description                                     | Value
-------------------------------------------|-------------------------------------------------|----------
LIFEGUARD\_RABBITMQ\_\w+\_ADMIN\_BASE\_URL   | RabbitMQ admin base url of default instance     | http://localhost:15672
LIFEGUARD\_RABBITMQ\_\w+\_ADMIN\_USER        | RabbitMQ admin user of default instance         | guest
LIFEGUARD\_RABBITMQ\_\w+\_ADMIN\_PASSWD      | RabbitMQ admin password of default instance     | guest
LIFEGUARD\_RABBITMQ\_\w+\_ADMIN\_VHOST       | RabbitMQ admin virtual host of default instance | /
LIFEGUARD\_RABBITMQ\_INSTANCES             | List of rabbitmq instances separated by comma   | default

## Builtin Validations

### Consumers Running Validation

Usage example:

```python
# in lifeguard_settings.py
from lifeguard_rabbitmq import RABBITMQ_PLUGIN_CONTEXT

from lifeguard import NORMAL, PROBLEM
from lifeguard.actions.email import send_email


RABBITMQ_PLUGIN_CONTEXT.consumers_validation_options = {
    "actions": [send_email],
    "schedule": {"every": {"minutes": 1}},
    "settings": {
        "email": {
            "subject": "[Lifeguard] - Consumers validation",
            "receivers": [{"name": "User", "email": "user@cserver.com"}],
            "send_in": [PROBLEM],
            "remove_from_sent_list_when": [NORMAL],
        }
    },
    "queues": {
        "default": [{"name": "lifeguard.queue.example", "min_number_of_consumers": 1}],
    },
}
```

### Messages Increasing Validation

Usage example:

```python
# in lifeguard_settings.py
from lifeguard_rabbitmq import RABBITMQ_PLUGIN_CONTEXT

from lifeguard import NORMAL, PROBLEM
from lifeguard.actions.database import save_result_into_database


RABBITMQ_PLUGIN_CONTEXT.messages_increasing_validation_options = {
    "actions": [save_result_into_database],
    "schedule": {"every": {"minutes": 1}},
    "settings": {},
    "queues": {
        "default": [{"name": "lifeguard.queue.example", "count_before_alert": 10}],
    },
}
```
