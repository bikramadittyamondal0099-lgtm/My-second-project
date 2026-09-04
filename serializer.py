import pickle


def serialize_function(function, args, kwargs):
    data = {
        "function": function,
        "args": args,
        "kwargs": kwargs
    }

    return pickle.dumps(data)


def deserialize_function(data):
    return pickle.loads(data)


def serialize_result(result):
    return pickle.dumps(result)


def deserialize_result(data):
    return pickle.loads(data)
