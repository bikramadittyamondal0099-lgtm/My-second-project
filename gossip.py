import asyncio
import os
import time
class Gossip:
    def __init__(self, node):
        self.node = node
        self.running = False
    def get_system_load(self):
        cpu = os.cpu_count() or 1
        try:
            load = os.getloadavg()[0]
            cpu_usage = min(100, round((load / cpu) * 100, 2))
        except:
            cpu_usage = 0
        return {
            "cpu": cpu_usage,
            "ram": 0,
            "timestamp": time.time()
        }
    async def broadcast_status(self):
        while self.running:
            status = self.get_system_load()
            self.node.load = status
            for peer_id, peer in self.node.dht.get_peers().items():
                message = {
                    "type": "GOSSIP",
                    "node_id": self.node.node_id,
                    "host": self.node.host,
                    "port": self.node.port,
                    "load": status
                }
                await self.node.network.send_message(
                    peer["host"],
                    peer["port"],
                    message
                )
            await asyncio.sleep(5)
    async def start(self):
        self.running = True
        asyncio.create_task(self.broadcast_status())
