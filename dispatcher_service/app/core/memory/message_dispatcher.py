import threading
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from ..logging_config import setup_custom_logger

import queue


class MessageDispatcher:
    def __init__(self, message_system, agent_registry, data_store, max_workers=5):
        """
        Initializes the MessageDispatcher.
        rabbitmq_system: An instance of RabbitMQConsistentHashSystem
                         (already bound to the x-consistent-hash exchange).

        Args:
            message_system: The messaging system instance used for inter-agent communication.
            agent_registry: A dictionary mapping agent names to their corresponding classes.
            data_store: A shared data store for agent outputs and shared data.
            logger: Logger instance for logging events.
        """
        self.message_system = message_system
        self.agent_registry = agent_registry
        self.data_store = data_store
        base_logger = setup_custom_logger("MessageDispatcher")
        self.logger = logging.LoggerAdapter(
            base_logger, extra={"chain_id": "N/A", "component": "Dispatcher"}
        )
        self.logger.info("MessageDispatcher initialized (x-consistent-hash)")

        self.stop_event = threading.Event()  # Event to signal the dispatcher to stop
        self.dispatcher_thread = None  # Thread will be initialized in start()

        self.cached_agents = {}
        self.chain_queues = defaultdict(queue.Queue)  # Separate queue per chain_id
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_chains = set()
        # We'll define _consume_thread in start()
        self._consume_thread = None

        # ------------------------ NEW LOCK ------------------------
        self._lock = threading.Lock()
        # ----------------------------------------------------------

    def start(self):
        """
        Starts the dispatcher in a separate thread (via RabbitMQ's start_consuming).
        """
        self.logger.info(
            "[MessageDispatcher] start() -> Using RabbitMQ x-consistent-hash system"
        )
        self.stop_event.clear()

        def message_callback(message):
            if not message:
                return

            try:
                # Message might be a list or a single dict
                if isinstance(message, list) and message:
                    chain_id = message[0]["chain_id"]
                    with self._lock:
                        for sub_msg in message:
                            self.chain_queues[chain_id].put(sub_msg)
                        if chain_id not in self.active_chains:
                            self.active_chains.add(chain_id)
                            self.executor.submit(self.dispatch_chain, chain_id)
                else:
                    chain_id = message["chain_id"]
                    with self._lock:
                        self.chain_queues[chain_id].put(message)
                        if chain_id not in self.active_chains:
                            self.active_chains.add(chain_id)
                            self.executor.submit(self.dispatch_chain, chain_id)

                self.logger.info(
                    f"[MessageDispatcher] Received message for chain {chain_id}: {message}"
                )

            except Exception as e:
                self.logger.error(f"Error processing message: {e}, message: {message}")

        # Start consuming in a background thread
        self._consume_thread = threading.Thread(
            target=self.message_system.start_consuming,
            args=(message_callback,),
            daemon=True,
        )
        self._consume_thread.start()

        self.logger.info(
            "[MessageDispatcher] Dispatcher is now consuming messages in the background"
        )

    def stop(self):
        """
        Signals the dispatcher to stop listening for messages and waits for the thread to finish.
        """
        self.stop_event.set()
        if self._consume_thread:
            # Give some time for in-progress messages to complete
            self._consume_thread.join(timeout=5.0)
        self.executor.shutdown(wait=True)

    def on_message_received(self, message):
        """
        If you manually use on_message_received, you can lock just like in start().
        """
        if isinstance(message, list) and message:
            chain_id = message[0].get("chain_id")
            if not chain_id:
                self.logger.error("No chain_id in the first item.")
                return

            with self._lock:
                for sub_msg in message:
                    self.chain_queues[chain_id].put(sub_msg)
                self.logger.info(
                    f"[MessageDispatcher] Received LIST for chain {chain_id}"
                )

                if chain_id not in self.active_chains:
                    self.active_chains.add(chain_id)
                    self.executor.submit(self.dispatch_chain, chain_id)

        else:
            chain_id = message.get("chain_id")
            if not chain_id:
                self.logger.error("Received message without chain_id, ignoring.")
                return
            with self._lock:
                self.chain_queues[chain_id].put(message)
                self.logger.info(
                    f"[MessageDispatcher] Received SINGLE for chain {chain_id}"
                )
                if chain_id not in self.active_chains:
                    self.active_chains.add(chain_id)
                    self.executor.submit(self.dispatch_chain, chain_id)

    def dispatch_chain(self, chain_id):
        """
        Process messages from this chain in order. We lock only around
        modifications to active_chains and chain_queues, not during the actual
        processing of each message, to avoid blocking other threads.
        """
        self.logger.info(f"[MessageDispatcher] Starting dispatch for chain {chain_id}")

        while not self.stop_event.is_set():
            with self._lock:
                q = self.chain_queues[chain_id]
                if q.empty():
                    # No messages left for this chain
                    break

                message = q.get()

            # We release the lock before dispatching the message to allow
            # other threads to enqueue or process other chains concurrently.

            try:
                self.dispatch_message(message)
            except Exception as e:
                self.logger.exception(
                    f"[MessageDispatcher] Error in chain {chain_id}: {e}"
                )
            finally:
                with self._lock:
                    q.task_done()

        # After we've emptied the queue or the stop_event is set,
        # we can safely remove the chain from active_chains.
        with self._lock:
            if chain_id in self.active_chains:
                self.active_chains.remove(chain_id)

            # Double-check if new messages arrived right after we removed chain_id
            # from active_chains, but only if we're not stopping.
            if not self.stop_event.is_set() and not self.chain_queues[chain_id].empty():
                # If the queue isn't empty, we re-add the chain to active_chains
                # and process again
                if chain_id not in self.active_chains:
                    self.active_chains.add(chain_id)
                    self.executor.submit(self.dispatch_chain, chain_id)
            else:
                # If truly empty now, we can safely remove the queue
                del self.chain_queues[chain_id]
                self.logger.info(
                    f"[MessageDispatcher] Finished dispatch for chain {chain_id}"
                )

    def dispatch_message(self, message):
        self.logger.info(
            f"[MessageDispatcher] Dispatching message test {type(message)} {message}"
        )

        chain_id = message["chain_id"]
        to_agent = message["to_agent"]

        self.logger.info(
            f"[MessageDispatcher] Dispatching message to agent='{to_agent}' in chain='{chain_id}'"
        )

        agent_cls = self.agent_registry.get(to_agent)
        if not agent_cls:
            self.logger.error(f"Agent '{to_agent}' not found for chain '{chain_id}'")
            return

        # Check agent cache
        agent_key = (chain_id, to_agent)
        if agent_key in self.cached_agents:
            agent_instance = self.cached_agents[agent_key]
        else:
            agent_instance = agent_cls(
                self.logger, message, self.data_store, self.message_system
            )
            self.cached_agents[agent_key] = agent_instance

        agent_instance.execute()
        self.logger.info(
            f"[MessageDispatcher] Agent '{to_agent}' for chain '{chain_id}' finished execution"
        )
