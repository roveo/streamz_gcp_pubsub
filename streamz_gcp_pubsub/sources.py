from google.api_core.exceptions import AlreadyExists
from google.cloud.pubsub import SubscriberClient
from streamz import Source
from streamz.core import RefCounter


def create_metadata(_id, ack):
    return [{"ref": RefCounter(cb=lambda: ack(_id))}]


class from_gcp_pubsub(Source):
    """Consume messages from a GCP PubSub subscription."""

    def __init__(
        self,
        subscription,
        max_messages: int = 1000,
        timeout: float = None,
        ensure_subscription: bool = False,
        topic: str = None,
        service_account_file: str = None,
        service_account_json: str = None,
        **kwargs
    ):
        """
        Authentication built into Google Cloud python package is used. If
        ``service_account_file`` is set, it will be used, otherwise
        ``service_account_json``. If both are ``None``, the library will look up
        service account file path in ``GOOGLE_APPLICATION_CREDENTIALS`` environment
        variable.

        Parameters
        ----------
        subscription: str
            Subscription path in the format
            ``projects/{project_name}/subscriptions/{subscription_name}``.
        max_messages: int
            Maximum number of messages that will be consumed at once. Defaults to 1000.
        timeout: float
            Number of seconds to wait for messages when none are available for the
            subscription. Will emit an empty list of messages afterwards. When ``None``,
            the source will block until there are messages to consume. Note that if you
            call ``stop()``, the source will stop only after it stops waiting for
            messages. Defaults to ``None``.
        ensure_subscription: bool
            Create subscription if it doesn't exist. If ``True``, then ``topic``
            parameter is required. Defaults to ``False``.
        topic: str
            Topic path for creating a subscription. Required if
            ``ensure_subscription=True``. Defaults to ``None``.
        service_account_file: str
            Path to a service account file used for authentication. Defaults to
            ``None``.
        service_account_json: str
            String representation of JSON data in service account file used for
            authentication. Defaults to ``None``.
        """
        super().__init__(ensure_io_loop=True, **kwargs)
        self._subscription = subscription
        self._max_messages = max_messages
        self._timeout = timeout
        self._ensure = ensure_subscription
        self._topic = topic
        self._client = self._create_client(service_account_file, service_account_json)

    def start(self):
        if self._ensure:
            if self._topic is not None:
                self._ensure_subscription()
            else:
                raise ValueError("topic is required when ensure_subscription=True")
        self.stopped = False
        self.loop.add_callback(self._run)

    async def _run(self):
        while not self.stopped:
            res = await self.loop.run_in_executor(None, self._pull)
            for item in res.received_messages:
                m = create_metadata(item.ack_id, ack=self._ack)
                await self.emit(item.message, metadata=m, asynchronous=True)
        self.stopped = True

    def _pull(self):
        return self._client.pull(
            subscription=self._subscription,
            max_messages=self._max_messages,
            timeout=self._timeout,
        )

    def _ack(self, *ids):
        self._client.acknowledge(subscription=self._subscription, ack_ids=ids)

    @staticmethod
    def _create_client(service_account_file=None, service_account_json=None):
        if service_account_file is not None:
            return SubscriberClient.from_service_account_file(service_account_file)
        if service_account_json is not None:
            return SubscriberClient.from_service_account_json(service_account_json)
        return SubscriberClient()

    def _ensure_subscription(self):
        try:
            self._client.create_subscription(name=self._subscription, topic=self._topic)
        except AlreadyExists:
            pass
