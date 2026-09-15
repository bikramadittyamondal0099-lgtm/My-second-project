import hashlib
import hmac
import json
import os


SECRET = os.environ.get(
    "MESHWEAVER_SECRET",
    "meshweaver-demo-secret"
).encode()


def create_signature(
    message
):

    clean_message = dict(
        message
    )

    clean_message.pop(
        "signature",
        None
    )

    data = json.dumps(
        clean_message,
        sort_keys=True,
        separators=(
            ",",
            ":"
        )
    ).encode()

    return hmac.new(
        SECRET,
        data,
        hashlib.sha256
    ).hexdigest()


def sign_message(
    message
):

    return create_signature(
        message
    )


def verify_message(
    message,
    signature
):

    expected = create_signature(
        message
    )

    return hmac.compare_digest(
        expected,
        signature
    )