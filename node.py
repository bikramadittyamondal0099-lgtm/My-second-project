import asyncio
import base64
import time

from dht import DHT
from gossip import Gossip
from heartbeat import HeartbeatMonitor
from network import Network
from security import sign_message, verify_message
from serializer import deserialize_result
from serializer import deserialize_task
from serializer import serialize_result
from task import TaskManager


class Node:

    def __init__(self, host, port, bootstrap=None):

        self.host = host
        self.port = int(port)

        self.bootstrap = bootstrap

        self.node_id = None

        self.network = Network(self)

        self.dht = DHT(self)

        self.gossip = Gossip(self)

        self.heartbeat = HeartbeatMonitor(self)

        self.tasks = TaskManager(self)

        self.load = {
            "cpu": 0.0,
            "ram": 0.0,
            "timestamp": 0
        }

        self.running = False

    async def start(self):

        self.node_id = self.dht.generate_node_id(
            self.host,
            self.port
        )

        self.running = True

        print("=" * 60)
        print("              MESHWEAVER")
        print("        P2P ASYNC TASK BROKER")
        print("=" * 60)

        print(f"Node ID : {self.node_id}")
        print(f"Address : {self.host}:{self.port}")

        print("=" * 60)

        await self.network.start()

        if self.bootstrap:

            await self.join_network(
                self.bootstrap[0],
                self.bootstrap[1]
            )

        await self.gossip.start()

        await self.heartbeat.start()

        print("[Node] Node started successfully.")

        print(
            f"[Node] Known peers: "
            f"{self.dht.peer_count()}"
        )

    async def stop(self):

        self.running = False

        await self.gossip.stop()

        await self.heartbeat.stop()

        await self.network.stop()

    async def join_network(self, host, port):

        print(
            f"[DHT] Connecting to "
            f"{host}:{port}"
        )

        response = await self.network.send_message(
            host,
            port,
            {
                "type": "JOIN",

                "node_id": self.node_id,

                "host": self.host,

                "port": self.port
            }
        )

        if not response:

            print(
                "[DHT] Bootstrap node unavailable."
            )

            return False

        bootstrap_id = response.get(
            "bootstrap_node_id"
        )

        if bootstrap_id:

            self.dht.add_peer(
                bootstrap_id,
                host,
                port,
                response.get("bootstrap_load")
            )

        for peer in response.get(
            "peers",
            []
        ):

            self.dht.add_peer(
                peer["node_id"],
                peer["host"],
                peer["port"],
                peer.get("load")
            )

        print(
            f"[DHT] Discovered "
            f"{self.dht.peer_count()} peer(s)"
        )

        await self.discover_more_peers()

        return True

    async def discover_more_peers(self):

        peers = list(
            self.dht.peers().values()
        )

        old_count = self.dht.peer_count()

        for peer in peers:

            response = await self.network.send_message(
                peer["host"],
                peer["port"],
                {
                    "type": "FIND_NODE",

                    "node_id": self.node_id,

                    "target_id": self.node_id
                }
            )

            if not response:
                continue

            for found in response.get(
                "peers",
                []
            ):

                self.dht.add_peer(
                    found["node_id"],
                    found["host"],
                    found["port"],
                    found.get("load")
                )

        print(
            f"[DHT] Total peers: "
            f"{self.dht.peer_count()} "
            f"(new="
            f"{self.dht.peer_count() - old_count})"
        )

    async def handle_message(self, message):

        message_type = message.get(
            "type"
        )

        if message_type == "PING":

            return {
                "type": "PONG",

                "node_id": self.node_id
            }

        if message_type == "JOIN":

            return self.handle_join(
                message
            )

        if message_type == "FIND_NODE":

            return self.handle_find_node(
                message
            )

        if message_type == "GOSSIP":

            return self.handle_gossip(
                message
            )

        if message_type == "TASK":

            return await self.handle_task(
                message
            )

        return {
            "type": "ERROR",

            "message": "Unknown message"
        }

    def handle_join(self, message):

        self.dht.add_peer(
            message["node_id"],
            message["host"],
            message["port"]
        )

        print(
            "[DHT] New peer joined: "
            f"{message['node_id'][:12]}"
        )

        peers = self.dht.closest(
            message["node_id"],
            self.dht.K
        )

        return {
            "type": "JOIN_RESPONSE",

            "bootstrap_node_id":
                self.node_id,

            "bootstrap_load":
                self.load,

            "peers": [
                {
                    "node_id": peer["node_id"],
                    "host": peer["host"],
                    "port": peer["port"],
                    "load": peer.get("load")
                }

                for peer in peers
            ]
        }

    def handle_find_node(self, message):

        peers = self.dht.closest(
            message.get(
                "target_id",
                self.node_id
            ),
            self.dht.K
        )

        return {
            "type": "PEERS",

            "peers": [
                {
                    "node_id": peer["node_id"],
                    "host": peer["host"],
                    "port": peer["port"],
                    "load": peer.get("load")
                }

                for peer in peers
            ]
        }

    def handle_gossip(self, message):

        node_id = message["node_id"]

        load = message.get(
            "load",
            {}
        )

        self.dht.add_peer(
            node_id,
            message.get(
                "host",
                "127.0.0.1"
            ),
            message.get(
                "port",
                0
            ),
            load
        )

        self.heartbeat.mark_seen(
            node_id
        )

        print(
            f"[Gossip] Received "
            f"{node_id[:8]} -> "
            f"CPU={load.get('cpu', 0)}% "
            f"RAM={load.get('ram', 0)}%"
        )

        return {
            "type": "GOSSIP_ACK"
        }

    async def handle_task(self, message):

        signature = message.get(
            "signature",
            ""
        )

        if not verify_message(
            message,
            signature
        ):

            return {
                "type": "TASK_ERROR",

                "task_id":
                    message.get(
                        "task_id"
                    ),

                "error":
                    "Invalid task signature"
            }

        try:

            payload = base64.b64decode(
                message["payload"]
            )

            task = deserialize_task(
                payload
            )

            print(
                "[Task] Executing "
                f"{message['task_id'][:12]}"
            )

            result = task["function"](
                *task["args"],
                **task["kwargs"]
            )

            encoded_result = base64.b64encode(
                serialize_result(result)
            ).decode("ascii")

            return {
                "type": "TASK_RESULT",

                "task_id":
                    message["task_id"],

                "result":
                    encoded_result
            }

        except Exception as error:

            return {
                "type": "TASK_ERROR",

                "task_id":
                    message.get(
                        "task_id"
                    ),

                "error":
                    str(error)
            }

    def available_workers(self):

        workers = []

        current_time = time.time()

        for peer in self.dht.peers().values():

            load = peer.get(
                "load",
                {}
            )

            timestamp = load.get(
                "timestamp",
                0
            )

            if current_time - timestamp <= 20:

                workers.append(peer)

        return workers

    def select_worker(
        self,
        excluded=None
    ):

        if excluded is None:
            excluded = set()

        workers = [
            peer

            for peer in self.available_workers()

            if peer["node_id"]
            not in excluded
        ]

        if not workers:
            return None

        return min(
            workers,

            key=lambda peer: (
                peer.get(
                    "load",
                    {}
                ).get(
                    "cpu",
                    100
                ),

                peer.get(
                    "load",
                    {}
                ).get(
                    "ram",
                    100
                )
            )
        )

    async def submit_task(
        self,
        function,
        *args,
        **kwargs
    ):

        record = self.tasks.create_task(
            function,
            *args,
            **kwargs
        )

        attempted = set()

        while True:

            worker = self.select_worker(
                attempted
            )

            if not worker:
                break

            attempted.add(
                worker["node_id"]
            )

            record.attempts += 1

            record.assigned_to = (
                worker["node_id"]
            )

            record.status = "RUNNING"

            message = {

                "type": "TASK",

                "task_id":
                    record.task_id,

                "payload":
                    record.payload
            }

            message["signature"] = sign_message(
                message
            )

            print(
                f"[Router] Task "
                f"{record.task_id[:8]} -> "
                f"{worker['node_id'][:8]} "
                f"(CPU="
                f"{worker.get('load', {}).get('cpu', 0)}%)"
            )

            response = await self.network.send_message(
                worker["host"],
                worker["port"],
                message,
                timeout=8
            )

            if response and response.get(
                "type"
            ) == "TASK_RESULT":

                result = deserialize_result(
                    base64.b64decode(
                        response["result"]
                    )
                )

                record.status = "COMPLETED"

                record.result = result

                print(
                    f"[Task] COMPLETED -> "
                    f"{result}"
                )

                return result

            print(
                "[FaultTolerance] "
                f"Worker {worker['node_id'][:8]} "
                "failed. Re-routing..."
            )

            self.dht.remove_peer(
                worker["node_id"]
            )

        record.status = "FAILED"

        record.error = (
            "No worker completed the task."
        )

        print("[Task] FAILED")

        return None

    async def handle_peer_failure(
        self,
        node_id
    ):

        for record in self.tasks.tasks.values():

            if (
                record.assigned_to == node_id
                and record.status == "RUNNING"
            ):

                record.status = "FAILED"

                record.error = (
                    "Assigned worker disappeared."
                )

                print(
                    f"[FaultTolerance] "
                    f"Task {record.task_id[:8]} "
                    "lost its worker."
                )