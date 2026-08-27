import asyncio
import base64

from network import Network
from dht import DHT
from gossip import Gossip
from serializer import deserialize_function, serialize_result
from task import TaskManager


class Node:
    def __init__(self, host, port, bootstrap=None):
        self.host = host
        self.port = port

        self.node_id = None
        self.bootstrap = bootstrap

        self.network = Network(self)
        self.dht = DHT(self)
        self.gossip = Gossip(self)
        self.task_manager = TaskManager(self)

        self.load = {
            "cpu": 0,
            "ram": 0
        }

    async def start(self):
        self.node_id = self.dht.generate_node_id(
            self.host,
            self.port
        )

        print()
        print("=" * 50)
        print("MeshWeaver Node")
        print("=" * 50)
        print(f"Node ID : {self.node_id[:16]}")
        print(f"Address : {self.host}:{self.port}")

        await self.network.start_server()
        await self.gossip.start()

        if self.bootstrap:
            await self.join_network(
                self.bootstrap[0],
                self.bootstrap[1]
            )

        print("[Node] Started successfully")
        print()

    async def join_network(self, host, port):
        print(f"[DHT] Joining network through {host}:{port}")

        message = {
            "type": "JOIN",
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port
        }

        response = await self.network.send_message(
            host,
            port,
            message
        )

        if response:
            peers = response.get("peers", [])

            for peer in peers:
                self.dht.add_peer(
                    peer["node_id"],
                    peer["host"],
                    peer["port"]
                )

            print(
                f"[DHT] Discovered {len(peers)} peer(s)"
            )

    async def handle_message(self, message):
        message_type = message.get("type")

        if message_type == "PING":
            return {
                "type": "PONG",
                "node_id": self.node_id
            }

        if message_type == "JOIN":
            return await self.handle_join(message)

        if message_type == "FIND_NODE":
            return self.handle_find_node()

        if message_type == "GOSSIP":
            return self.handle_gossip(message)

        if message_type == "TASK":
            return await self.handle_task(message)

        return {
            "type": "ERROR",
            "message": "Unknown message type"
        }

    async def handle_join(self, message):
        node_id = message["node_id"]
        host = message["host"]
        port = message["port"]

        self.dht.add_peer(
            node_id,
            host,
            port
        )

        print(
            f"[DHT] New peer joined: {node_id[:16]}"
        )

        peers = []

        for peer_id, peer in self.dht.get_peers().items():
            peers.append({
                "node_id": peer_id,
                "host": peer["host"],
                "port": peer["port"]
            })

        return {
            "type": "JOIN_RESPONSE",
            "peers": peers
        }

    def handle_find_node(self):
        peers = []

        for peer_id, peer in self.dht.get_peers().items():
            peers.append({
                "node_id": peer_id,
                "host": peer["host"],
                "port": peer["port"]
            })

        return {
            "type": "PEERS",
            "peers": peers
        }

    def handle_gossip(self, message):
        node_id = message["node_id"]

        if node_id in self.dht.routing_table:
            self.dht.routing_table[node_id]["load"] = message["load"]

        print(
            f"[Gossip] {node_id[:8]} -> "
            f"CPU: {message['load']['cpu']}%"
        )

        return {
            "type": "GOSSIP_ACK"
        }

    async def handle_task(self, message):
        task_id = message["task_id"]

        try:
            encoded_payload = message["payload"]
            payload = base64.b64decode(encoded_payload)

            task_data = deserialize_function(payload)

            function = task_data["function"]
            args = task_data["args"]
            kwargs = task_data["kwargs"]

            print(f"[Task] Executing {task_id}")

            result = function(*args, **kwargs)

            result_data = serialize_result(result)
            encoded_result = base64.b64encode(
                result_data
            ).decode()

            return {
                "type": "TASK_RESULT",
                "task_id": task_id,
                "result": encoded_result
            }

        except Exception as e:
            return {
                "type": "TASK_ERROR",
                "task_id": task_id,
                "error": str(e)
            }

    async def ping(self, host, port):
        message = {
            "type": "PING",
            "node_id": self.node_id
        }

        return await self.network.send_message(
            host,
            port,
            message
        )

    async def submit_task(self, function, *args, **kwargs):
        task = self.task_manager.create_task(
            function,
            *args,
            **kwargs
        )

        peers = self.dht.get_peers()

        if not peers:
            print("[Task] No peers available")
            return None

        selected_peer_id = min(
            peers,
            key=lambda peer_id:
                peers[peer_id].get("load", {}).get("cpu", 0)
        )

        peer = peers[selected_peer_id]

        print(
            f"[Task] Sending {task['task_id']} "
            f"to {selected_peer_id[:16]}"
        )

        message = {
            "type": "TASK",
            "task_id": task["task_id"],
            "payload": task["payload"]
        }

        response = await self.network.send_message(
            peer["host"],
            peer["port"],
            message
        )

        if response:
            if response["type"] == "TASK_RESULT":
                data = base64.b64decode(
                    response["result"]
                )

                from serializer import deserialize_result

                result = deserialize_result(data)

                print(f"[Task] Result: {result}")

                return result

            print(
                f"[Task] Failed: "
                f"{response.get('error')}"
            )

        return None