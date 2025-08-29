from setuptools import find_packages, setup

setup(
    name="ra_netsuite_shared_utils",
    version="0.6.5",
    author="Vrishabh Agamya",
    packages=find_packages(),
    install_requires=[
        "requests",
        "requests-oauthlib",
        "google-cloud-storage",
        "google-cloud-pubsub",
        "google-cloud-tasks",
    ],
)
