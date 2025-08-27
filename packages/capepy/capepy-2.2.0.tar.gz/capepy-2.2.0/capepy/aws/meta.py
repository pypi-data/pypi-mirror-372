import logging

import boto3


class Boto3Object(object):
    """Contains general resources needed by all AWS utilities for interacting with the boto3 library

    Attributes:
        logger: The logger for logging to AWS Glue
        clients: A dictionary of instantiated AWS clients indexed by the name of the AWS service.
        resources: A dictionary of instantiated AWS resources indexed by the name of the AWS service.
    """

    def __init__(self):
        """Constructor for initializing a Boto3Object"""
        self.logger = logging.getLogger(__name__)
        self.clients = {}
        self.resources = {}

    def get_client(self, service_name: str, **kwargs):
        """Get a client for the provided service, if one hasn't been created yet, set a new client.

        Args:
            service_name: The name of the service to retrieve a client for.
            **kwargs: Optional keyword arguments passed to `boto3.client()` if a new client needs to be set.

        Returns:
            The boto3 client.
        """
        if service_name not in self.clients:
            self.set_client(service_name, **kwargs)
        return self.clients[service_name]

    def set_client(self, service_name: str, **kwargs):
        """Set a new client for the provided service.

        Args:
            service_name: The name of the service to instantiate a new client
            for.
            **kwargs: Optional keyword arguments passed to `boto3.client()`.
        """
        self.clients[service_name] = boto3.client(
            service_name, **kwargs  # pyright: ignore
        )

    def get_resource(self, service_name: str, **kwargs):
        """Get a resource for the provided service, if one hasn't been created yet, set a new resource.

        Args:
            service_name: The name of the service to retrieve a resource for.
            **kwargs: Optional keyword arguments passed to `boto3.resource()` if a new resource needs to be set.

        Returns:
            The boto3 client.
        """
        if service_name not in self.resources:
            self.set_resource(service_name, **kwargs)
        return self.resources[service_name]

    def set_resource(self, service_name: str, **kwargs):
        """Set a new resource for the provided service.

        Args:
            service_name: The name of the service to instantiate a new resource for.
            **kwargs: Optional keyword arguments passed to `boto3.resource()`.
        """
        self.resources[service_name] = boto3.resource(
            service_name, **kwargs  # pyright: ignore
        )
