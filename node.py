import asyncio
import base64

from network import Network
from dht import DHT
from gossip import Gossip
from serializer import (
    deserialize_function,
    serialize_result,
    deserialize_result
)
from task import TaskManager


class Node:

    def __init__(
        self,
        host,
        port,
        bootstrap=None
    ):

        self.host = host
        self.port = port

        self.node_id = None

        self.bootstrap = bootstrap

        self.network = Network(self)

        self.dht = DHT(self)

        self.gossip = Gossip(self)

        self.task_manager = TaskManager(
            self
        )

        self.load = {
            "cpu": 0,
            "ram": 0,
            "timestamp": 0
        }

    # ==================================================
    # START NODE
    # ==================================================

    async def start(self):

        self.node_id = (
            self.dht.generate_node_id(
                self.host,
                self.port
            )
        )

        print()
        print("=" * 60)
        print("              MESHWEAVER NODE")
        print("=" * 60)

        print(
            f"Node ID : {self.node_id}"
        )

        print(
            f"Address : "
            f"{self.host}:{self.port}"
        )

        print(
            "Mode    : "
            "Kademlia-style P2P + Gossip"
        )

        print("=" * 60)

        await self.network.start_server()

        await self.gossip.start()

        if self.bootstrap:

            await self.join_network(
                self.bootstrap[0],
                self.bootstrap[1]
            )

        print(
            "[Node] Node started successfully."
        )

        print()

    # ==================================================
    # JOIN NETWORK
    # ==================================================

    async def join_network(
        self,
        host,
        port
    ):

        print(
            f"[DHT] Connecting to "
            f"{host}:{port}"
        )

        message = {

            "type": "JOIN",

            "node_id":
                self.node_id,

            "host":
                self.host,

            "port":
                self.port
        }

        response = (
            await self.network
            .send_message(
                host,
                port,
                message
            )
        )

        if not response:

            print(
                "[DHT] Bootstrap node "
                "did not respond."
            )

            return

        # Add bootstrap node
        bootstrap_id = (
            response.get(
                "bootstrap_node_id"
            )
        )

        if bootstrap_id:

            self.dht.add_peer(
                bootstrap_id,
                host,
                port,
                response.get(
                    "bootstrap_load"
                )
            )

        # Add returned peers
        peers = response.get(
            "peers",
            []
        )

        for peer in peers:

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

        # Ask discovered nodes for
        # more peers.
        await self.discover_more_peers()

    # ==================================================
    # PEER DISCOVERY
    # ==================================================

    async def discover_more_peers(self):

        peers = list(
            self.dht
            .get_peers()
            .values()
        )

        discovered_count = 0

        for peer in peers:

            message = {

                "type":
                    "FIND_NODE",

                "node_id":
                    self.node_id,

                "target_id":
                    self.node_id
            }

            response = (
                await self.network
                .send_message(
                    peer["host"],
                    peer["port"],
                    message
                )
            )

            if not response:
                continue

            discovered = response.get(
                "peers",
                []
            )

            for new_peer in discovered:

                before = (
                    self.dht.peer_count()
                )

                self.dht.add_peer(
                    new_peer["node_id"],
                    new_peer["host"],
                    new_peer["port"],
                    new_peer.get("load")
                )

                after = (
                    self.dht.peer_count()
                )

                if after > before:

                    discovered_count += 1

        print(
            f"[DHT] Additional peers "
            f"discovered: "
            f"{discovered_count}"
        )

        print(
            f"[DHT] Total peers: "
            f"{self.dht.peer_count()}"
        )

    # ==================================================
    # MESSAGE HANDLER
    # ==================================================

    async def handle_message(
        self,
        message
    ):

        message_type = (
            message.get("type")
        )

        if message_type == "PING":

            return {

                "type":
                    "PONG",

                "node_id":
                    self.node_id
            }

        if message_type == "JOIN":

            return await self.handle_join(
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

            "type":
                "ERROR",

            "message":
                "Unknown message type"
        }

    # ==================================================
    # HANDLE JOIN
    # ==================================================

    async def handle_join(
        self,
        message
    ):

        node_id = message["node_id"]

        host = message["host"]

        port = message["port"]

        self.dht.add_peer(
            node_id,
            host,
            port
        )

        print(
            f"[DHT] New peer joined: "
            f"{node_id[:16]}"
        )

        # Return closest peers
        closest = (
            self.dht.find_closest_nodes(
                target_id=node_id,
                count=self.dht.K
            )
        )

        peers = []

        for peer in closest:

            peers.append({

                "node_id":
                    peer["node_id"],

                "host":
                    peer["host"],

                "port":
                    peer["port"],

                "load":
                    peer.get("load")
            })

        return {

            "type":
                "JOIN_RESPONSE",

            "bootstrap_node_id":
                self.node_id,

            "bootstrap_load":
                self.load,

            "peers":
                peers
        }

    # ==================================================
    # FIND NODE
    # ==================================================

    def handle_find_node(
        self,
        message
    ):

        target_id = message.get(
            "target_id",
            self.node_id
        )

        closest = (
            self.dht.find_closest_nodes(
                target_id=target_id,
                count=self.dht.K
            )
        )

        peers = []

        for peer in closest:

            peers.append({

                "node_id":
                    peer["node_id"],

                "host":
                    peer["host"],

                "port":
                    peer["port"],

                "load":
                    peer.get("load")
            })

        return {

            "type":
                "PEERS",

            "peers":
                peers
        }

    # ==================================================
    # GOSSIP
    # ==================================================

    def handle_gossip(
        self,
        message
    ):

        node_id = message[
            "node_id"
        ]

        load = message.get(
            "load",
            {}
        )

        added = self.dht.add_peer(

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

        if not added:

            self.dht.update_peer_load(
                node_id,
                load
            )

        print(
            f"[Gossip] "
            f"{node_id[:8]} -> "
            f"CPU {load.get('cpu', 0)}% | "
            f"RAM {load.get('ram', 0)}%"
        )

        return {
            "type":
                "GOSSIP_ACK"
        }

    # ==================================================
    # TASK EXECUTION
    # ==================================================

    async def handle_task(
        self,
        message
    ):

        task_id = message[
            "task_id"
        ]

        try:

            encoded_payload = (
                message["payload"]
            )

            payload = (
                base64.b64decode(
                    encoded_payload
                )
            )

            task_data = (
                deserialize_function(
                    payload
                )
            )

            function = (
                task_data["function"]
            )

            args = (
                task_data["args"]
            )

            kwargs = (
                task_data["kwargs"]
            )

            print(
                f"[Task] Executing "
                f"{task_id}"
            )

            result = function(
                *args,
                **kwargs
            )

            result_data = (
                serialize_result(
                    result
                )
            )

            encoded_result = (
                base64.b64encode(
                    result_data
                ).decode()
            )

            return {

                "type":
                    "TASK_RESULT",

                "task_id":
                    task_id,

                "result":
                    encoded_result
            }

        except Exception as e:

            return {

                "type":
                    "TASK_ERROR",

                "task_id":
                    task_id,

                "error":
                    str(e)
            }

    # ==================================================
    # PING
    # ==================================================

    async def ping(
        self,
        host,
        port
    ):

        response = (
            await self.network
            .send_message(
                host,
                port,
                {
                    "type":
                        "PING",

                    "node_id":
                        self.node_id
                }
            )
        )

        return response

    # ==================================================
    # SUBMIT TASK
    # ==================================================

    async def submit_task(
        self,
        function,
        *args,
        **kwargs
    ):

        task = (
            self.task_manager
            .create_task(
                function,
                *args,
                **kwargs
            )
        )

        peers = self.dht.get_peers()

        if not peers:

            print(
                "[Task] No peers available."
            )

            return None

        # Select lowest CPU node.
        selected_peer_id = min(

            peers,

            key=lambda peer_id:

                peers[peer_id]
                .get(
                    "load",
                    {}
                )
                .get(
                    "cpu",
                    0
                )
        )

        peer = peers[
            selected_peer_id
        ]

        print(
            f"[Task] Selected peer: "
            f"{selected_peer_id[:16]}"
        )

        print(
            f"[Task] CPU load: "
            f"{peer.get('load', {}).get('cpu', 0)}%"
        )

        self.task_manager.update_status(
            task["task_id"],
            "RUNNING"
        )

        response = (
            await self.network
            .send_message(

                peer["host"],

                peer["port"],

                {
                    "type":
                        "TASK",

                    "task_id":
                        task["task_id"],

                    "payload":
                        task["payload"]
                }
            )
        )

        if not response:

            self.task_manager.update_status(
                task["task_id"],
                "FAILED"
            )

            return None

        if response["type"] == "TASK_RESULT":

            data = (
                base64.b64decode(
                    response["result"]
                )
            )

            result = (
                deserialize_result(
                    data
                )
            )

            self.task_manager.update_status(
                task["task_id"],
                "COMPLETED"
            )

            print(
                f"[Task] Result: "
                f"{result}"
            )

            return result

        self.task_manager.update_status(
            task["task_id"],
            "FAILED"
        )

        print(
            f"[Task] Failed: "
            f"{response.get('error')}"
        )

        return None
