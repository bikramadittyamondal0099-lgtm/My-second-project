import asyncio
import sys

from node import Node


def square_sum(a, b):
    return a * a + b * b


async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("python main.py 5001")
        print("python main.py 5002 5001")
        return

    port = int(sys.argv[1])

    bootstrap = None

    if len(sys.argv) >= 3:
        bootstrap = (
            "127.0.0.1",
            int(sys.argv[2])
        )

    node = Node(
        "127.0.0.1",
        port,
        bootstrap
    )

    await node.start()

    if bootstrap:
        await asyncio.sleep(3)

        result = await node.submit_task(
            square_sum,
            10,
            20
        )

        print(f"[Main] Final result: {result}")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n[Node] Shutting down...")
if __name__ == "__main__":
    asyncio.run(main())