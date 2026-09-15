import asyncio


class HeartbeatMonitor:

    INTERVAL = 5

    def __init__(self, node):

        self.node = node

        self.running = False

        self.task = None

        self.last_seen = {}

    def mark_seen(
        self,
        node_id
    ):

        import time

        self.last_seen[node_id] = (
            time.time()
        )

    def mark_failed(
        self,
        node_id
    ):

        self.last_seen[node_id] = 0

    async def loop(self):

        while self.running:

            peers = list(
                self.node.dht.peers().values()
            )

            for peer in peers:

                response = (
                    await
                    self.node.network.send_message(
                        peer["host"],
                        peer["port"],
                        {
                            "type":
                                "PING",

                            "node_id":
                                self.node.node_id
                        },
                        timeout=2
                    )
                )

                if response:

                    self.mark_seen(
                        peer["node_id"]
                    )

                else:

                    print(
                        "[Heartbeat] "
                        f"Peer failed: "
                        f"{peer['node_id'][:8]}"
                    )

                    self.node.dht.remove_peer(
                        peer["node_id"]
                    )

                    await self.node.handle_peer_failure(
                        peer["node_id"]
                    )

            await asyncio.sleep(
                self.INTERVAL
            )

    async def start(self):

        self.running = True

        self.task = asyncio.create_task(
            self.loop()
        )

    async def stop(self):

        self.running = False

        if self.task:

            self.task.cancel()

            try:

                await self.task

            except asyncio.CancelledError:
                pass