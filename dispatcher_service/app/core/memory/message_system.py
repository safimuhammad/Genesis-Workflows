import pika
import json
import logging
from ..logging_config import setup_custom_logger


class RabbitMQMessageSystem:
    """
    A RabbitMQ-based message system that uses an x-consistent-hash exchange.
    This allows multiple consumers (queues) to be bound with weights, so all messages
    sharing the same routing key (e.g., chain_id) go to exactly one queue.
    """

    def __init__(self, amqp_url, exchange_name, queue_name=None, weight=1):
        """
        amqp_url:        e.g. "amqp://guest:guest@rabbitmq:5672/%2F"
        exchange_name:   The name of the x-consistent-hash exchange to declare/bind.
        queue_name:      Optional. If not provided, we'll get a unique queue name from the broker.
        weight:          The binding weight for this queue (as a string).
                        If you have more powerful consumers, you might use '2' or '3'.
        """
        self.logger = logging.LoggerAdapter(
            setup_custom_logger("RabbitMQConsistentHashSystem"),
            extra={"chain_id": "N/A", "component": "RabbitMQConsistentHashSystem"},
        )
        self.logger.info("Initializing RabbitMQConsistentHashSystem")

        self.ampq_url = amqp_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.weight = weight

        self.connection = pika.BlockingConnection(pika.URLParameters(self.ampq_url))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="x-consistent-hash", durable=True
        )

        if queue_name:
            self.queue_name = queue_name
            self.channel.queue_declare(queue=self.queue_name, durable=True)
        else:
            result = self.channel.queue_declare(
                queue="", exclusive=False, auto_delete=False
            )
            self.queue_name = result.method.queue

        self.channel.queue_bind(
            queue=self.queue_name,
            exchange=self.exchange_name,
            routing_key=str(self.weight)
        )
        self.channel.basic_qos(prefetch_count=10)
        self.logger.info(
            f"[RabbitMQConsistentHashSystem] Bound queue='{self.queue_name}' "
            f"to exchange='{self.exchange_name}' with weight='{self.weight}'"
        )

    def publish_message(self, chain_id, message_list):
        """
        Publish a message to the x-consistent-hash exchange, using `chain_id` as the routing key.
        All messages with the same chain_id will end up in exactly one bound queue.
        """
        body = json.dumps(message_list)
        routing_key = str(chain_id)
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,  # The x-consistent-hash exchange uses this for hashing
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),  # persistent
        )
        self.logger.info(
            f"[RabbitMQConsistentHashSystem] Published to exchange='{self.exchange_name}', "
            f"chain_id='{chain_id}', message={message_list}"
        )

    def receive_one(self, timeout=1):
        """
        An optional helper if you want to pull a single message from your queue (not recommended for scale).
        In a real x-consistent-hash system, you typically run `basic_consume` + start_consuming in a thread.
        """
        method_frame, header_frame, body = self.channel.basic_get(
            queue=self.queue_name, auto_ack=False
        )
        if not method_frame:
            return None

        try:
            msg_str = body.decode("utf-8")
            message = json.loads(msg_str)
        except Exception as e:
            self.logger.error(f"Failed to decode message: {body}, error: {e}")
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return None

        self.logger.info(f"[RabbitMQConsistentHashSystem] Received message: {message}")
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        return message

    def start_consuming(self, on_message_callback):
        """
        A blocking method to continuously consume messages.
        Typically you'd run this in a separate thread or process.
        """
        self.logger.info("[RabbitMQConsistentHashSystem] Starting to consume...")

        def callback(ch, method, properties, body):
            try:
                msg_str = body.decode("utf-8")
                message = json.loads(msg_str)
                on_message_callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self.logger.exception(f"Error in consumer callback: {e}")
                # Possibly do ch.basic_nack(...) to requeue or dead-letter

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=False
        )
        self.channel.start_consuming()

    def close(self):
        """
        Cleanly close the connection.
        """
        self.logger.info(
            f"[RabbitMQConsistentHashSystem] Closing connection for queue={self.queue_name}"
        )
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()
