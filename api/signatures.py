from hashlib import sha256


def calculate_event_signature(data):
    message = None

    if (
        "exception" in data
        and data["exception"]
        and data["exception"]["values"]
    ):
        message = data["exception"]["values"][0]["type"]
    elif (
        "logentry" in data
        and data["logentry"]
        and data["logentry"]["message"]
    ):
        message = data["logentry"]["message"]
    elif "message" in data and data["message"]:
        message = data["message"]

    return (
        sha256(message.encode()).hexdigest()
        if message is not None
        else None
    )
