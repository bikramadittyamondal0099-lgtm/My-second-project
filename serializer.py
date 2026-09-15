import pickle


try:

    import cloudpickle

except ImportError:

    cloudpickle = None


def dumps(obj):

    if cloudpickle:

        return cloudpickle.dumps(
            obj
        )

    return pickle.dumps(
        obj
    )


def loads(data):

    if cloudpickle:

        return cloudpickle.loads(
            data
        )

    return pickle.loads(
        data
    )


def serialize_task(
    function,
    args,
    kwargs
):

    data = {

        "function":
            function,

        "args":
            args,

        "kwargs":
            kwargs
    }

    return dumps(
        data
    )


def deserialize_task(
    data
):

    return loads(
        data
    )


def serialize_result(
    result
):

    return dumps(
        result
    )


def deserialize_result(
    data
):

    return loads(
        data
    )