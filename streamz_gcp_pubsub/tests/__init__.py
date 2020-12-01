from uuid import uuid4


def uuid(n=None):
    if n is None:
        return "test_" + str(uuid4())
    return ["test_" + str(uuid4()) for _ in range(n)]
