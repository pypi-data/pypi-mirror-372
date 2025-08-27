import codecs
import os.path

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="netbox-sync-status",
    version=get_version("netbox_sync_status/version.py"),
    description="Sync Status for netbox objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jysk-network/netbox-sync-status",
    author="Patrick Falk Nielsen",
    author_email="panie@jysk.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ]
)
