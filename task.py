import base64
import uuid
from dataclasses import dataclass

from serializer import serialize_task


@dataclass
class TaskRecord:

    task_id: str

    payload: str

    status: str = "PENDING"

    assigned_to: str = None

    attempts: int = 0

    result: object = None

    error: str = None


class TaskManager:

    def __init__(self, node):

        self.node = node

        self.tasks = {}

    def create_task(
        self,
        function,
        *args,
        **kwargs
    ):

        task_id = str(
            uuid.uuid4()
        )

        data = serialize_task(
            function,
            args,
            kwargs
        )

        encoded = base64.b64encode(
            data
        ).decode("ascii")

        record = TaskRecord(
            task_id=task_id,

            payload=encoded
        )

        self.tasks[task_id] = record

        return record

    def get_task(
        self,
        task_id
    ):

        return self.tasks.get(
            task_id
        )

    def update_status(
        self,
        task_id,
        status
    ):

        record = self.tasks.get(
            task_id
        )

        if record:

            record.status = status