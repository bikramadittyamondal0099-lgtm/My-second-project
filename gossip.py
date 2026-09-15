import asyncio
import os
import sys
import time


class SystemMonitor:

    def __init__(self):

        self.last_cpu = None

    def cpu_percent(self):

        if sys.platform == "win32":

            try:

                import ctypes

                class FILETIME(
                    ctypes.Structure
                ):

                    _fields_ = [
                        (
                            "dwLowDateTime",
                            ctypes.c_ulong
                        ),

                        (
                            "dwHighDateTime",
                            ctypes.c_ulong
                        )
                    ]

                idle = FILETIME()
                kernel = FILETIME()
                user = FILETIME()

                result = (
                    ctypes.windll.kernel32
                    .GetSystemTimes
                )(
                    ctypes.byref(idle),
                    ctypes.byref(kernel),
                    ctypes.byref(user)
                )

                if result:

                    def value(filetime):

                        return (
                            filetime.dwHighDateTime
                            << 32
                        ) + filetime.dwLowDateTime

                    idle_now = value(idle)

                    total_now = (
                        value(kernel)
                        +
                        value(user)
                    )

                    if self.last_cpu:

                        old_idle, old_total = (
                            self.last_cpu
                        )

                        idle_delta = (
                            idle_now
                            -
                            old_idle
                        )

                        total_delta = (
                            total_now
                            -
                            old_total
                        )

                        self.last_cpu = (
                            idle_now,
                            total_now
                        )

                        if total_delta:

                            cpu = (
                                100
                                *
                                (
                                    1
                                    -
                                    idle_delta
                                    /
                                    total_delta
                                )
                            )

                            return round(
                                max(
                                    0,
                                    min(
                                        100,
                                        cpu
                                    )
                                ),
                                2
                            )

                    self.last_cpu = (
                        idle_now,
                        total_now
                    )

            except Exception:
                pass

        try:

            if hasattr(
                os,
                "getloadavg"
            ):

                load = os.getloadavg()[0]

                cpu_count = (
                    os.cpu_count()
                    or 1
                )

                return round(
                    min(
                        100,
                        load /
                        cpu_count *
                        100
                    ),
                    2
                )

        except Exception:
            pass

        return 0.0

    @staticmethod
    def ram_percent():

        try:

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

                status = MEMORYSTATUSEX()

                status.dwLength = (
                    ctypes.sizeof(
                        MEMORYSTATUSEX
                    )
                )

                ctypes.windll.kernel32 \
                    .GlobalMemoryStatusEx(
                        ctypes.byref(status)
                    )

                return float(
                    status.dwMemoryLoad
                )

        except Exception:
            pass

        return 0.0


class Gossip:

    INTERVAL = 5

    def __init__(self, node):

        self.node = node

        self.monitor = SystemMonitor()

        self.running = False

        self.task = None

    def current_load(self):

        return {

            "cpu":
                self.monitor.cpu_percent(),

            "ram":
                self.monitor.ram_percent(),

            "timestamp":
                time.time()
        }

    async def loop(self):

        while self.running:

            load = self.current_load()

            self.node.load = load

            peers = list(
                self.node.dht.peers().values()
            )

            print(
                f"[Gossip] "
                f"CPU={load['cpu']}% "
                f"RAM={load['ram']}% "
                f"Peers={len(peers)}"
            )

            message = {

                "type":
                    "GOSSIP",

                "node_id":
                    self.node.node_id,

                "host":
                    self.node.host,

                "port":
                    self.node.port,

                "load":
                    load
            }

            for peer in peers:

                response = (
                    await
                    self.node.network.send_message(
                        peer["host"],
                        peer["port"],
                        message,
                        timeout=2
                    )
                )

                if response is None:

                    self.node.heartbeat.mark_failed(
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