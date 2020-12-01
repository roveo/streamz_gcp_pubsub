from setuptools import setup


setup(
    name="streamz_gcp_pubsub",
    version="0.1.0",
    install_requires=["streamz", "google-cloud-pubsub"],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "docs": ["sphinx"],
    },
    entry_points={
        "streamz.sources": [
            "from_gcp_pubsub = streamz_gcp_pubsub.sources:from_gcp_pubsub"
        ]
    },
)
