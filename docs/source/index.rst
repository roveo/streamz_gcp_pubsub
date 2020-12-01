streamz_gcp_pubsub
==================

This plugin adds a single source: ``from_gcp_pubsub``, that allows you to consume
messages from a Google Cloud PubSub subscription.

Installation
------------

.. code-block:: shell

   pip install git+https://github.com/roveo/streamz_gcp_pubsub.git

Example usage
-------------

.. code-block:: python

   import time
   from streamz import Stream

   source = Stream.from_gcp_pubsub(
      "projects/example-project/subscriptions/test-sub",
      service_account_file="/path/to/service_account_file.json",
   )
   source.map(lambda x: x.data.decode()).map(json.loads).sink(print)

   if __name__ == "__main__":
      source.start()
      while True:
         time.sleep(10)


API
---

.. autoclass:: streamz_gcp_pubsub.sources.from_gcp_pubsub
   :members: __init__

.. toctree::
   :maxdepth: 2
   :caption: Contents:
