#!/usr/bin/env python
import json
import time
from core.memory.message_system import RabbitMQMessageSystem
import uuid
import random


def test_publish_message():
    # RabbitMQ connection details should match those in your main.py
    amqp_url = "amqp://guest:guest@localhost:5672/%2F"
    exchange_name = "chain_consistent_hash_ex"

    rabbitmq_system = RabbitMQMessageSystem(
        amqp_url=amqp_url,
        exchange_name=exchange_name,
        queue_name="dispatcher_queue_1",
    )

    # Generate and publish 500 messages
    for i in range(500):
        chain_id = str(uuid.uuid4())
        message_chain = [
            {
                "from_agent": "user",
                "to_agent": "read_file",
                "message": f"read the file {i}",
                "args": [
                    {
                        "arg_name": "file_path",
                        "arg_value": "topic.txt",
                        "is_static": True,
                    }
                ],
                "chain_id": chain_id,
            },
            {
                "from_agent": "read_file",
                "to_agent": "write_file",
                "message": "Write the content to file",
                "args": [
                    {
                        "arg_name": "file_path",
                        "arg_value": f"chain{i}-out.md",
                        "is_static": True,
                    },
                    {"arg_name": "data", "arg_value": "None", "is_static": False},
                ],
                "chain_id": chain_id,
            },
        ]
        # time.sleep(1)

        # Use the chain_id directly from the first message
        rabbitmq_system.publish_message(message_chain[0]["chain_id"], message_chain)
        print(f"Published message {i+1}/500 with chain_id '{chain_id}'")

    # Give some time for the message to be processed
    print("All messages published. Waiting for 30 seconds before closing connection...")
    time.sleep(200)
    rabbitmq_system.close()


if __name__ == "__main__":
    test_publish_message()
