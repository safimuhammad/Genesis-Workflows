import sys
import time
from core.memory.message_dispatcher import MessageDispatcher
from core.memory.message_system import RabbitMQMessageSystem
from core.memory.datastore import Datastore
from core.agent import WriteAgent, ReadAgent, ContentWriter


def main():
    amqp_url = "amqp://guest:guest@localhost:5672/%2F"
    exchange_name = "chain_consistent_hash_ex"
    queue_name = "dispatcher_queue_1"
    message_system = RabbitMQMessageSystem(
        amqp_url=amqp_url,
        exchange_name=exchange_name,
        queue_name=queue_name,
        weight="1",
    )

    data_store = Datastore()
    agent_registry = {
        "content_writer": ContentWriter,
        "write_file": WriteAgent,
        "read_file": ReadAgent,
    }

    dispatcher = MessageDispatcher(
        message_system=message_system,
        agent_registry=agent_registry,
        data_store=data_store,
        max_workers=20,
    )

    dispatcher.start()
    print("Dispatcher started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping dispatcher...")
        dispatcher.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
