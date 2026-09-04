import asyncio
import os
import sys
import time


class Gossip:

    INTERVAL = 5

    def __init__(self, node):

        self.node = node
        self.running = False
        self.task = None

    # --------------------------------------------------
    # CPU
    # --------------------------------------------------

    def get_cpu_usage(self):

        try:

            # Linux / Unix
            if hasattr(os, "getloadavg"):

                load = os.getloadavg()[0]

                cpu_count = os.cpu_count() or 1

                usage = (
                    load / cpu_count
                ) * 100

                return round(
                    min(100, usage),
                    2
                )

        except Exception:
            pass

        # Windows fallback
        return 0.0

    # --------------------------------------------------
    # RAM
    # --------------------------------------------------

    def get_ram_usage(self):

        try:

            # Windows
            if sys.platform == "win32":

                import ctypes

                class MEMORYSTATUSEX(
                    ctypes.Structure
                ):

                    _fields_ = [
                        (
                            "dwLength",
                            ctypes.c_ulong
                        ),
                        (
                            "dwMemoryLoad",
                            ctypes.c_ulong
                        ),
                        (
                            "ullTotalPhys",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullAvailPhys",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullTotalPageFile",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullAvailPageFile",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullTotalVirtual",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullAvailVirtual",
                            ctypes.c_ulonglong
                        ),
                        (
                            "ullAvailExtendedVirtual",
                            ctypes.c_ulonglong
                        )
                    ]

                memory = MEMORYSTATUSEX()

                memory.dwLength = (
                    ctypes.sizeof(
                        MEMORYSTATUSEX
                    )
                )

                result = (
                    ctypes.windll.kernel32
                    .GlobalMemoryStatusEx(
                        ctypes.byref(memory)
                    )
                )

                if result:

                    return float(
                        memory.dwMemoryLoad
                    )

            # Linux
            if sys.platform.startswith("linux"):

                values = {}

                with open(
                    "/proc/meminfo",
                    "r"
                ) as file:

                    for line in file:

                        parts = line.split()

                        if len(parts) >= 2:

                            key = parts[0].rstrip(":")

                            values[key] = int(
                                parts[1]
                            )

                total = values.get(
                    "MemTotal",
                    0
                )

                available = values.get(
                    "MemAvailable",
                    0
                )

                if total:

                    used = (
                        total - available
                    )

                    return round(
                        (used / total) * 100,
                        2
                    )

        except Exception:
            pass

        return 0.0

    # --------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------

    def get_system_load(self):

        return {
            "cpu": self.get_cpu_usage(),
            "ram": self.get_ram_usage(),
            "timestamp": time.time()
        }

    # --------------------------------------------------
    # GOSSIP BROADCAST
    # --------------------------------------------------

    async def broadcast_status(self):

        while self.running:

            status = (
                self.get_system_load()
            )

            self.node.load = status

            peers = list(
                self.node.dht
                .get_peers()
                .values()
            )

            print(
                f"[Gossip] "
                f"CPU: {status['cpu']}% | "
                f"RAM: {status['ram']}% | "
                f"Peers: {len(peers)}"
            )

            for peer in peers:

                message = {

                    "type": "GOSSIP",

                    "node_id":
                        self.node.node_id,

                    "host":
                        self.node.host,

                    "port":
                        self.node.port,

                    "load":
                        status
                }

                response = (
                    await self.node.network
                    .send_message(
                        peer["host"],
                        peer["port"],
                        message
                    )
                )

                # If peer doesn't respond,
                # remove it from routing table.
                if response is None:

                    print(
                        f"[Gossip] "
                        f"Peer offline: "
                        f"{peer['node_id'][:8]}"
                    )

                    self.node.dht.remove_peer(
                        peer["node_id"]
                    )

            await asyncio.sleep(
                self.INTERVAL
            )

    # --------------------------------------------------
    # START
    # --------------------------------------------------

    async def start(self):

        if self.running:
            return

        self.running = True

        self.task = asyncio.create_task(
            self.broadcast_status()
        )

    # --------------------------------------------------
    # STOP
    # --------------------------------------------------

    async def stop(self):

        self.running = False

        if self.task:

            self.task.cancel()

            try:
                await self.task

            except asyncio.CancelledError:
                pass
