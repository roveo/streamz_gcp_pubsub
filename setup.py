from setuptools import setup, find_packages


setup(
    name="streamz_gcp_pubsub",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "streamz @ git+https://github.com/python-streamz/streamz.git",
        "google-cloud-pubsub",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "docs": ["sphinx", "sphinx_rtd_theme"],
    },
    entry_points={
        "streamz.sources": [
            "from_gcp_pubsub = streamz_gcp_pubsub.sources:from_gcp_pubsub"
        ]
    },
)
