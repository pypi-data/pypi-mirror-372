from botocore.exceptions import ClientError


def decode_error(err: ClientError):
    """Decode a client error message from AWS

    Args:
        err: The ClientError to parse out the error code and message if they are
        available.

    Returns:
        A tuple (code, message) where code is a string containing the error
        code, and message is a string containing the entire error message.
    """
    code, message = "Unknown", "Unknown"
    if "Error" in err.response:
        error = err.response["Error"]
        if "Code" in error:
            code = error["Code"]
        if "Message" in error:
            message = error["Message"]
    return code, message
