import traceback

from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)

from lifeguard.logger import lifeguard_logger as logger

from lifeguard_rabbitmq.settings import SETTINGS_MANAGER
from lifeguard_rabbitmq.validations import CONSUMERS


class RabbitMQConsumer:
    def __init__(self):
        self.channel = None

        # controls
        self.finished = False
        self.initied = False

        parameters = ConnectionParameters(
            host=SETTINGS_MANAGER.read_value("LIFEGUARD_RABBITMQ_HOST"),
            virtual_host=SETTINGS_MANAGER.read_value("LIFEGUARD_RABBITMQ_VHOST"),
            credentials=PlainCredentials(
                SETTINGS_MANAGER.read_value("LIFEGUARD_RABBITMQ_USER"),
                SETTINGS_MANAGER.read_value("LIFEGUARD_RABBITMQ_PASSWD"),
            ),
        )

        self.connection = BlockingConnection(parameters=parameters)
        channel = self.connection.channel()

        self.build_channel(channel)

    def build_channel(self, channel):
        arguments = {}

        self.channel = channel
        self.channel.basic_qos(prefetch_count=1)
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)
        for _, consumer in CONSUMERS.items():
            self.channel.queue_declare(
                queue=consumer["queue"],
                durable=consumer["durable"],
                exclusive=consumer["exclusive"],
                auto_delete=consumer["auto_delete"],
                arguments=arguments,
            )

            self.channel.queue_bind(
                exchange=consumer["exchange"],
                queue=consumer["queue"],
                routing_key=consumer["routing_key"],
            )

            def consumer_callback(ch, method, properties, body):
                self.handle_delivery(ch, method, properties, body, consumer["ref"])

            self.channel.basic_consume(consumer["queue"], consumer_callback)

    def handle_delivery(self, channel, method, header, body, on_receive):
        """
        Method is called when message is consumed
        :param _channel: channel connection
        :param method: method object
        :param header: header message
        :param body: body message
        """

        extra = {}
        try:
            logger_message = "receiving message %s" % (body.decode("utf-8"))
            data = body.decode("utf-8")

            logger.info(logger_message, extra=extra)
            on_receive(data, header.headers, extra)
            channel.basic_ack(method.delivery_tag)
        except Exception as error:
            channel.basic_nack(method.delivery_tag, requeue=False)
            extra["traceback"] = traceback.format_exc()
            traceback.print_exc()
            logger.error("error on consume message: %s", str(error), extra=extra)

    def start(self):
        logger.info("starting consumer for queues")
        self.initied = True
        try:
            self.channel.start_consuming()
        except Exception as error:
            self.finished = True
            logging.error("error on consumer: %s", str(error))

    def on_consumer_cancelled(self):
        logging.error("consumer cancelled")
        self.finished = True
        self.channel.stop_consuming()
