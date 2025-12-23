"""
============================================================================
FILE: packages/zemrev-queue/setup.py
PURPOSE: Shared queue package for all ZEMREV services
============================================================================
"""

from setuptools import setup, find_packages

setup(
    name="zemrev-queue",
    version="1.0.0",
    description="Shared Redis queue manager for ZEMREV microservices",
    author="ZEMREV",
    packages=find_packages(),
    install_requires=[
        "redis[hiredis]==5.0.1",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
    ],
    python_requires=">=3.11",
)