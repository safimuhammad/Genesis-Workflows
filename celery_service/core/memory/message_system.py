import pika
from ..logging_config import setup_custom_logger
import logging
import json

class RabbitMQMessageSystem:
    def __init__(self, amqp_url, queue_name):
        """
        amqp_url: e.g. 'amqp://guest:guest@localhost:5672/'
        queue_name: Name of the queue to send/receive from
        """
        self.logger = logging.LoggerAdapter(
            setup_custom_logger("RabbitMQMessageSystem"),
            extra={'chain_id': 'N/A', 'component': 'RabbitMQMessageSystem'}
        )
        self.logger.info("Initializing RabbitMQMessageSystem")

        self.amqp_url = amqp_url
        self.queue_name = queue_name

        # Create connection/channel
        self.connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        self.channel = self.connection.channel()

        # Ensure the queue exists
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def send(self, message):
        """
        Publishes a message to the RabbitMQ queue.
        `message` should be a dict (so we can JSON-encode it).
        """
        self.logger.info(f"[RabbitMQMessageSystem] Sending message: {message}")
        body = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )

    def receive(self, timeout=5):
        """
        Attempts to pull one message from RabbitMQ using basic_get. 
        If no message is available, returns None.
        
        'timeout' can be used in a more advanced consumer scenario, but with basic_get 
        it won't truly block. We'll just attempt a get and if none is there, we return None.
        """
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=False)
        if method_frame:
            # We got a message
            message_str = body.decode('utf-8')
            try:
                message = json.loads(message_str)
            except json.JSONDecodeError:
                self.logger.error(f"Failed to decode message: {message_str}")
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return None

            self.logger.info(f"[RabbitMQMessageSystem] Received message: {message}")
            # Acknowledge the message
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return message

        # No message
        return None

    def close(self):
        """
        Cleanly close the connection. 
        """
        self.connection.close()

        
# class InMemoryMessageSystem:
#     def __init__(self):
#         self.queue = queue.Queue()
#         base_logger = setup_custom_logger("InMemoryMessageSystem")
#         self.logger = logging.LoggerAdapter(
#             base_logger,
#             extra={'chain_id': 'N/A', 'component': 'InMemoryMessageSystem'}
#         )
#         self.logger.info("InMemoryMessageSystem started")

#     def send(self, message):
#         self.queue.put(message)
#         self.logger.info(f"[InMemoryMessageSystem] Sending message {message}")

#     def receive(self, timeout=0):
#         try:
#             message = self.queue.get(timeout=timeout)
#             self.logger.info(f"[InMemoryMessageSystem] receiving message {message}")
#             return message
#         except queue.Empty:
#             return None
