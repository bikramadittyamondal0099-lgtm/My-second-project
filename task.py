import base64
import uuid

from serializer import serialize_function


class TaskManager:

    def __init__(self, node):
        self.node = node
        self.tasks = {}

    def create_task(self, function, *args, **kwargs):

        task_id = str(uuid.uuid4())

        payload = serialize_function(
            function,
            args,
            kwargs
        )

        encoded_payload = base64.b64encode(
            payload
        ).decode()

        task = {
            "task_id": task_id,
            "payload": encoded_payload,
            "status": "PENDING"
        }

        self.tasks[task_id] = task

        return task

    def update_status(self, task_id, status):

        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status

    def get_task(self, task_id):

        return self.tasks.get(task_id)
