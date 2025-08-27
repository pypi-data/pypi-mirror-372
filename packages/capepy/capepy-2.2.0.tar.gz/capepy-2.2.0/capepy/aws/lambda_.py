import json
from urllib.parse import unquote_plus


class Record(object):
    """An object for general records in AWS Lambda handlers.

    Attributes:
        raw: The raw record
    """

    def __init__(self, record):
        """Constructor for instantiating a new Lambda Record

        Args:
            record (object): A record from an AWS Lambda handler event
        """
        self.raw = record


class BucketNotificationRecord(Record):
    """An object for S3 bucket notification related records passed into AWS Lambda handlers.

    Attributes:
        bucket: The name of the bucket
        key: The key into the bucket if relevant
    """

    def __init__(self, record):
        """Constructor for instantiating a new record of S3 bucket information

        Args:
            record (object): An S3 bucket related record from an AWS Lambda handler event
        """
        super().__init__(record)
        self.bucket = self.raw["s3"]["bucket"]["name"]
        self.key = unquote_plus(
            self.raw["s3"]["object"]["key"], encoding="utf-8"
        )


class QueueRecord(Record):
    """An object for general records in AWS Lambda handlers.

    Attributes:
        raw: The raw record
    """

    def __init__(self, record):
        """Constructor for instantiating a new Lambda Record

        Args:
            record (object): A record from an AWS Lambda handler event
        """
        super().__init__(record)
        try:
            self.body = json.loads(self.raw["body"])
        except ValueError:
            self.body = self.raw["body"]
        self.id = self.raw["messageId"]


class EtlRecord(QueueRecord):
    """An object for ETL related records passed into AWS Lambda handlers.

    Attributes:
        job: The name of the ETL Job
        bucket: The name of the bucket
        key: The key into the bucket if relevant
    """

    def __init__(self, record):
        """Constructor for instantiating a new record of S3 bucket information

        Args:
            record (object): An S3 bucket related record from an AWS Lambda handler event
        """
        super().__init__(record)
        self.job = self.body["etl_job"]
        self.bucket = self.body["bucket"]
        self.key = self.body["key"]


class PipelineRecord(QueueRecord):
    """An object for pipeline records passed into AWS Lambda handlers.

    Attributes:
        name: The name of the analysis pipeline
        version: The version of the analysis pipeline
        parameters: A dictionary of parameters to pass to the analysis pipeline
    """

    def __init__(self, record):
        """Constructor for instantiating a new record of an analysis pipeline

        Args:
            record (object): An analysis pipeline related record from an AWS Lambda handler event
        """
        super().__init__(record)
        self.name = self.body["pipeline_name"]
        self.version = self.body["pipeline_version"]
        self.parameters = self.body["pipeline_parameters"]
