import asyncio
import json


class Network:
    def __init__(self, node):
        self.node = node
        self.server = None

    async def start_server(self):
        self.server = await asyncio.start_server(
            self.handle_connection,
            self.node.host,
            self.node.port
        )

        print(
            f"[Network] Listening on "
            f"{self.node.host}:{self.node.port}"
        )

    async def handle_connection(self, reader, writer):
        address = writer.get_extra_info("peername")

        try:
            data = await reader.readline()

            if not data:
                return

            message = json.loads(data.decode())

            response = await self.node.handle_message(message)

            if response is not None:
                writer.write(
                    (json.dumps(response) + "\n").encode()
                )
                await writer.drain()

        except Exception as e:
            print(f"[Network Error] {address}: {e}")

        finally:
            writer.close()

            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def send_message(self, host, port, message):
        writer = None

        try:
            reader, writer = await asyncio.open_connection(
                host,
                port
            )

            writer.write(
                (json.dumps(message) + "\n").encode()
            )

            await writer.drain()

            data = await asyncio.wait_for(
                reader.readline(),
                timeout=5
            )

            if data:
                return json.loads(data.decode())

        except Exception as e:
            print(
                f"[Connection Error] "
                f"{host}:{port} -> {e}"
            )

        finally:
            if writer:
                writer.close()

                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        return None
