import argparse
import asyncio
import threading
import time

from node import Node
from demo_tasks import square_sum, complex_math, matrix_sum
from ui import MeshWeaverUI


async def start_node(args):
    """Create and start a MeshWeaver node."""

    bootstrap = None

    if args.bootstrap:
        bootstrap = (
            "127.0.0.1",
            args.bootstrap
        )

    node = Node(
        host="127.0.0.1",
        port=args.port,
        bootstrap=bootstrap
    )

    await node.start()

    return node


def run_async_node(args, container):
    """
    Run the MeshWeaver asyncio event loop
    inside a background thread.
    """

    async def runner():

        # Get the SAME asyncio loop used by the node
        loop = asyncio.get_running_loop()

        container["loop"] = loop

        # Start MeshWeaver node
        node = await start_node(args)

        container["node"] = node

        try:
            # Keep the node alive
            await asyncio.Event().wait()

        finally:
            await node.stop()

    asyncio.run(runner())


async def run_demo(node):
    """Run demonstration tasks."""

    await asyncio.sleep(6)

    print(
        "\n[Demo] Running complex math task..."
    )

    await node.submit_task(
        complex_math,
        [2, 3, 4, 5, 6]
    )

    print(
        "\n[Demo] Running matrix task..."
    )

    await node.submit_task(
        matrix_sum,
        [
            [1, 2],
            [3, 4],
            [5, 6]
        ]
    )

    print(
        "\n[Demo] Running square_sum(10, 20)..."
    )

    await node.submit_task(
        square_sum,
        10,
        20
    )


def main():

    parser = argparse.ArgumentParser(
        description="MeshWeaver P2P Async Task Broker"
    )

    parser.add_argument(
        "port",
        type=int,
        help="Port of this node"
    )

    parser.add_argument(
        "bootstrap",
        type=int,
        nargs="?",
        help="Port of bootstrap node"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run distributed task demonstration"
    )

    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch MeshWeaver graphical dashboard"
    )

    args = parser.parse_args()

    # =========================================================
    # UI MODE
    # =========================================================

    if args.ui:

        container = {}

        # Start asyncio node in background
        node_thread = threading.Thread(
            target=run_async_node,
            args=(
                args,
                container
            ),
            daemon=True
        )

        node_thread.start()

        # Wait for node and event loop
        while (
            "node" not in container
            or "loop" not in container
        ):

            time.sleep(0.1)

        node = container["node"]
        node_loop = container["loop"]

        # Start Tkinter in main thread
        app = MeshWeaverUI(
            node,
            node_loop
        )

        app.run()

        return

    # =========================================================
    # NORMAL CLI MODE
    # =========================================================

    async def normal_mode():

        node = await start_node(
            args
        )

        try:

            if args.demo and args.bootstrap:

                await run_demo(
                    node
                )

            # Keep node alive
            await asyncio.Event().wait()

        finally:

            await node.stop()

    try:

        asyncio.run(
            normal_mode()
        )

    except KeyboardInterrupt:

        print(
            "\n[Node] MeshWeaver stopped."
        )


if __name__ == "__main__":
    main()