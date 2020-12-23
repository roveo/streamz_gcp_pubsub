import time

import pytest
from _pytest.outcomes import Failed
from streamz import Stream
from streamz.utils_test import wait_for
from streamz_gcp_pubsub.sources import from_gcp_pubsub
from streamz_gcp_pubsub.tests import uuid

Stream.register_api(staticmethod)(from_gcp_pubsub)


def test_source(clients, info):
    topic, subscription = info
    source = Stream.from_gcp_pubsub(subscription, timeout=1)
    L = source.map(lambda x: int(x.data)).sink_to_list()
    source.start()

    pub, _ = clients
    for i in range(10):
        pub.publish(topic, str(i).encode())

    wait_for(lambda: list(range(10)) == L, 1)

    with pytest.raises(Failed):
        wait_for(lambda: len(L) > 10, 3)  # test ack

    source.stop()


def test_ensure(clients, info):
    pub, sub = clients
    topic, _ = info

    sub_path = f"projects/test-project/subscriptions/test_{uuid()}"

    source = Stream.from_gcp_pubsub(
        sub_path, timeout=1, ensure_subscription=True, topic=topic
    )
    source.sink_to_list()
    source.start()

    subscriptions = set(
        s.name for s in sub.list_subscriptions(project="projects/test-project")
    )
    assert sub_path in subscriptions

    source.stop()


@pytest.mark.usefixtures("clients")
def test_ensure_raises():
    sub_path = f"projects/test-project/subscriptions/test_{uuid()}"

    source = Stream.from_gcp_pubsub(
        sub_path, timeout=1, ensure_subscription=True, topic=None
    )

    with pytest.raises(ValueError):
        source.start()


def test_ensure_idempotent(info):
    topic, subscription = info

    source = Stream.from_gcp_pubsub(
        subscription, timeout=1, ensure_subscription=True, topic=topic
    )
    source.start()  # sub already exists, but this shouldn't fail
    source.stop()


def test_timeout(info):
    topic, subscription = info

    source = Stream.from_gcp_pubsub(subscription, timeout=0.5)
    source.start()
    time.sleep(3)
    source.stop()
