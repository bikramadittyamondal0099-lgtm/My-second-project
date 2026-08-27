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

        print(f"[Network] Listening on {self.node.host}:{self.node.port}")

    async def handle_connection(self, reader, writer):
        try:
            data = await reader.readline()

            if not data:
                return

            message = json.loads(data.decode())
            response = await self.node.handle_message(message)

            if response:
                writer.write((json.dumps(response) + "\n").encode())
                await writer.drain()

        except Exception as e:
            print(f"[Network Error] {e}")

        finally:
            writer.close()
            await writer.wait_closed()

    async def send_message(self, host, port, message):
        try:
            reader, writer = await asyncio.open_connection(host, port)

            writer.write((json.dumps(message) + "\n").encode())
            await writer.drain()

            data = await reader.readline()

            writer.close()
            await writer.wait_closed()

            if data:
                return json.loads(data.decode())

        except Exception as e:
            print(f"[Connection Error] {host}:{port} -> {e}")

        return None