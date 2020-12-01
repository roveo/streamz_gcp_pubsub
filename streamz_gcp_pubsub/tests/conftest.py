import os
import shlex
import subprocess

import pytest
from google.cloud.pubsub import PublisherClient, SubscriberClient
from streamz.utils_test import wait_for
from streamz_gcp_pubsub.tests import uuid


PROJECT = "test-project"
CONTAINER = "test-streamz-gcp-pubsub"


def cleanup(fail=False):
    rm_cmd = shlex.split(f"docker rm -f {CONTAINER}")
    try:
        subprocess.check_call(rm_cmd)
    except subprocess.CalledProcessError as e:
        print(e)
        if fail:
            raise


@pytest.fixture(scope="session")
def clients():
    cleanup()
    run_cmd = shlex.split(
        f"docker run -d -p 8085:8085 --name {CONTAINER} google/cloud-sdk "
        "gcloud beta emulators pubsub start "
        f"--project={PROJECT} --host-port=0.0.0.0:8085"
    )
    subprocess.check_call(run_cmd)

    def predicate():
        cmd = shlex.split(f"docker logs {CONTAINER}")
        logs = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return b"INFO: Server started, listening on 8085" in logs

    wait_for(predicate, 10, period=0.1)
    os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"
    os.environ["PUBSUB_PROJECT_ID"] = PROJECT
    try:
        yield (PublisherClient(), SubscriberClient())
    finally:
        cleanup(fail=True)


@pytest.fixture(scope="function")
def info(clients):
    pub, sub = clients
    topic, subscription = uuid(2)

    topic_path = pub.topic_path(PROJECT, topic)
    pub.create_topic(name=topic_path)

    sub_path = sub.subscription_path(PROJECT, subscription)
    sub.create_subscription(name=sub_path, topic=topic_path, ack_deadline_seconds=1)

    return topic_path, sub_path
