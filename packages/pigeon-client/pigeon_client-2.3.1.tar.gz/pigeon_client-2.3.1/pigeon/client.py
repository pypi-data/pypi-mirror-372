import logging
import os
import socket
import time
from importlib.metadata import entry_points
from typing import Callable, Dict
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span
from py_zipkin.request_helpers import extract_zipkin_attrs_from_headers

import stomp
import stomp.exception
from pydantic import ValidationError
from stomp.utils import Frame

from . import messages
from . import exceptions
from .utils import (
    get_message_hash,
    call_with_correct_args,
    setup_zipkin_transport,
)


def get_str_time_ms():
    return str(int(time.time_ns() / 1e6))


class Pigeon:
    """A STOMP client with message definitions via Pydantic

    This class is a STOMP message client which will automatically serialize and
    deserialize message data using Pydantic models. Before sending or receiving
    messages, topics must be "registered", or in other words, have a Pydantic
    model associated with each STOMP topic that will be used. This can be done
    in two ways. One is to use the register_topic(), or register_topics()
    methods. The other is to have message definitions in a Python package
    with an entry point defined in the pigeon.msgs group. This entry point
    should provide a tuple containing a mapping of topics to Pydantic models.
    Topics defined in this manner will be automatically discovered and loaded at
    runtime, unless this mechanism is manually disabled.
    """

    def __init__(
        self,
        service: str,
        host: str = "127.0.0.1",
        port: int = 61616,
        logger: logging.Logger = None,
        load_topics: bool = True,
        create_zipkin_spans: bool = True,
        send_zipkin_headers: bool = True,
    ):
        """
        Args:
            service: The name of the service. This will be included in the
                message headers.
            host: The location of the STOMP message broker.
            port: The port to use when connecting to the STOMP message broker.
            logger: A Python logger to use. If not provided, a logger will be
                crated.
            load_topics: If true, load topics from Python entry points.
            create_zipkin_spans: If true, and required environment variables are present,
                configure Zipkin transport and create new spans for every received message.
            send_zipkin_headers: If true, attempt to send Zipkin span propogation headers.

        """
        self._service = service
        self._connection = stomp.Connection12([(host, port)], heartbeats=(10000, 10000))
        self._topics = {}
        self._hashes = {}
        if load_topics:
            self._load_topics()
        self._callbacks: Dict[str, Callable] = {}
        self._connection.set_listener(
            "listener", TEMCommsListener(self._handle_message)
        )
        self._logger = logger if logger is not None else logging.getLogger(__name__)

        self._pid = os.getpid()
        self._hostname = socket.gethostname().split(".")[0]
        self._name = f"{self._service}_{self._pid}_{self._hostname}"
        self.register_topics(messages.core_topics)

        self._zipkin_transport = None
        if create_zipkin_spans:
            self._zipkin_transport = setup_zipkin_transport()
        self._send_zipkin_headers = send_zipkin_headers

    def _announce(self, connected=True):
        self.send(
            "&_announce_connection",
            name=self._name,
            pid=self._pid,
            hostname=self._hostname,
            service=self._service,
            connected=connected,
        )

    def _update_state(self):
        self.send(
            "&_update_state",
            name=self._name,
            pid=self._pid,
            hostname=self._hostname,
            service=self._service,
            subscribed_to=list(self._callbacks.keys()),
        )

    def _load_topics(self):
        for entrypoint in entry_points(group="pigeon.msgs"):
            self.register_topics(entrypoint.load())

    def register_topic(self, topic: str, msg_class: Callable):
        """Register message definition for a given topic.

        Args:
            topic: The topic that this message definition applies to.
            msg_class: The Pydantic model definition of the message.
        """
        self._topics[topic] = msg_class
        self._hashes[topic] = get_message_hash(msg_class)

    def register_topics(self, topics: Dict[str, Callable]):
        """Register a number of message definitions for multiple topics.

        Args:
            topics: A mapping of topics to Pydantic model message definitions.
        """
        for topic in topics.items():
            self.register_topic(*topic)

    def connect(
        self,
        username: str = None,
        password: str = None,
        retry_limit: int = 8,
    ):
        """
        Connects to the STOMP server using the provided username and password.

        Args:
            username (str, optional): The username to authenticate with. Defaults to None.
            password (str, optional): The password to authenticate with. Defaults to None.
            retry_limit (int, optional): Number of times to attempt connection

        Raises:
            stomp.exception.ConnectFailedException: If the connection to the server fails.
        """
        retries = 0
        while retries < retry_limit:
            try:
                self._connection.connect(
                    username=username, passcode=password, wait=True
                )
                self._logger.info("Connected to STOMP server.")
                break
            except stomp.exception.ConnectFailedException as e:
                self._logger.error(f"Connection failed: {e}. Attempting to reconnect.")
                retries += 1
                time.sleep(1)
                if retries == retry_limit:
                    raise stomp.exception.ConnectFailedException(
                        f"Could not connect to server: {e}"
                    ) from e

        self.subscribe("&_request_state", self._update_state)
        self._announce()

    def send(self, topic: str, **data):
        """
        Sends data to the specified topic.

        Args:
            topic (str): The topic to send the data to.
            **data: Keyword arguments representing the data to be sent.

        Raises:
            exceptions.NoSuchTopicException: If the specified topic is not defined.
        """
        self._ensure_topic_exists(topic)
        serialized_data = self._topics[topic](**data).serialize()

        headers = dict(
            source=self._name,
            service=self._service,
            hostname=self._hostname,
            pid=self._pid,
            hash=self._hashes[topic],
            sent_at=get_str_time_ms(),
        )
        if self._send_zipkin_headers:
            headers.update(create_http_headers_for_new_span())
        self._connection.send(destination=topic, body=serialized_data, headers=headers)
        self._logger.debug(f"Sent data to {topic}: {serialized_data[:1000]}")

    def _ensure_topic_exists(self, topic: str):
        if topic not in self._topics or topic not in self._hashes:
            raise exceptions.NoSuchTopicException(f"Topic {topic} not defined.")

    def _handle_message(self, message_frame: Frame):
        topic = message_frame.headers["subscription"]
        if topic not in self._topics or topic not in self._hashes:
            self._logger.warning(
                f"Received a message on an unregistered topic: {topic}"
            )
            return
        if message_frame.headers.get("hash") != self._hashes.get(topic):
            self._logger.warning(
                f"Received a message on topic '{topic}' with an incorrect hash: {message_frame.headers.get('hash')}. Expected: {self._hashes.get(topic)}"
            )
            return
        try:
            message_data = self._topics[topic].deserialize(message_frame.body)
        except ValidationError as e:
            self._logger.warning(
                f"Failed to deserialize message on topic '{topic}' with error:\n{e}"
            )
            return
        callback = self._callbacks.get(topic)
        if callback is None:
            self._logger.warning(
                f"No callback for message received on topic '{topic}'."
            )
            return
        try:
            self.with_zipkin_span_from_headers(
                message_frame.headers,
                call_with_correct_args,
                callback,
                message_data,
                topic,
                message_frame.headers,
            )
        except exceptions.SignatureException as e:
            self._logger.warning(
                f"Callback signature for topic '{topic}' not acceptable. Call failed with error:\n{e}"
            )
        except Exception as e:
            self._logger.warning(
                f"Callback for topic '{topic}' failed with error:", exc_info=True
            )

    def with_zipkin_span_from_headers(self, headers, function, *args, **kwargs):
        if (
            self._zipkin_transport is None
            or (zipkin_attrs := extract_zipkin_attrs_from_headers(headers)) is None
        ):
            return function(*args, **kwargs)
        else:
            with zipkin_span(
                service_name=self._service,
                span_name=f"handle {headers['subscription']}",
                transport_handler=self._zipkin_transport,
                zipkin_attrs=zipkin_attrs,
            ):
                return function(*args, **kwargs)

    def subscribe(self, topic: str, callback: Callable, send_update=True):
        """
        Subscribes to a topic and associates a callback function to handle incoming messages.

        Args:
            topic (str): The topic to subscribe to.
            callback (Callable): The callback function to handle incoming
                messages. It may accept up to three arguments. In order, the
                arguments are, the received message, the topic the message was
                received on, and the message headers.

        Raises:
            NoSuchTopicException: If the specified topic is not defined.
        """
        self._ensure_topic_exists(topic)
        if topic not in self._callbacks:
            self._connection.subscribe(destination=topic, id=topic)
        self._callbacks[topic] = callback
        self._logger.info(f"Subscribed to {topic} with {callback}.")
        if send_update:
            self._update_state()

    def subscribe_all(self, callback: Callable, include_core=False):
        """Subscribes to all registered topics.

        Args:
            callback: The function to call when a message is received. It must
                accept two arguments, the topic and the message data.
            include_core (bool): If true, subscribe all will subscribe the client to core messages.
        """

        # Additional logic here is to avoid subscribe_all changing behavior and always subscribing to core topics.
        if (
            len([topic for topic in self._topics if topic not in messages.core_topics])
            == 0
        ):
            self._logger.warning("No non-system topics registered!")
        for topic in self._topics:
            if topic in messages.core_topics and not include_core:
                continue
            if topic == "&_request_state":
                continue
            self.subscribe(topic, callback, send_update=False)
        self._update_state()

    def unsubscribe(self, topic: str):
        """Unsubscribes from a given topic.

        Args:
            topic: The topic to unsubscribe from."""
        self._ensure_topic_exists(topic)
        self._connection.unsubscribe(id=topic)
        self._logger.info(f"Unsubscribed from {topic}.")
        del self._callbacks[topic]

    def disconnect(self):
        """Disconnect from the STOMP message broker."""
        if self._connection.is_connected():
            self._announce(connected=False)
            self._connection.disconnect()
            self._logger.info("Disconnected from STOMP server.")


class TEMCommsListener(stomp.ConnectionListener):
    def __init__(self, callback: Callable):
        self.callback = callback

    def on_message(self, frame):
        frame.headers["received_at"] = get_str_time_ms()
        self.callback(frame)
