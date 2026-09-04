import asyncio
import sys
from node import Node
def square_sum(a, b):

    return (
        a * a
        +
        b * b
    )
def complex_calculation(numbers):

    total = 0

    for number in numbers:

        total += (
            number ** 2
        )

    return {
        "count": len(numbers),
        "sum_of_squares": total
    }


# ==========================================
# MAIN
# ==========================================

async def main():

    if len(sys.argv) < 2:

        print()
        print("MeshWeaver")
        print()
        print("Usage:")
        print()
        print(
            "  python main.py 5001"
        )

        print(
            "  python main.py 5002 5001"
        )

        print(
            "  python main.py 5003 5001"
        )

        print()

        return

    port = int(
        sys.argv[1]
    )

    bootstrap = None

    if len(sys.argv) >= 3:

        bootstrap = (

            "127.0.0.1",

            int(
                sys.argv[2]
            )
        )

    node = Node(

        "127.0.0.1",

        port,

        bootstrap
    )

    await node.start()

    # ======================================
    # TEST REMOTE TASK
    # ======================================

    if bootstrap:

        await asyncio.sleep(5)

        print()
        print(
            "[Main] Testing remote task..."
        )

        result = await node.submit_task(

            square_sum,

            10,

            20
        )

        print(
            f"[Main] Final result: "
            f"{result}"
        )

        print()

    # ======================================
    # KEEP NODE RUNNING
    # ======================================

    try:

        await asyncio.Event().wait()

    except KeyboardInterrupt:

        print(
            "\n[Node] Shutting down..."
        )

        await node.gossip.stop()


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
