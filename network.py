import asyncio
import json


class Network:

    def __init__(self, node):

        self.node = node

        self.server = None

    async def start(self):

        self.server = await asyncio.start_server(
            self.handle_connection,

            self.node.host,

            self.node.port
        )

        print(
            f"[Network] Listening on "
            f"{self.node.host}:"
            f"{self.node.port}"
        )

    async def handle_connection(
        self,
        reader,
        writer
    ):

        try:

            data = await asyncio.wait_for(
                reader.readline(),
                timeout=10
            )

            if not data:
                return

            message = json.loads(
                data.decode()
            )

            response = await self.node.handle_message(
                message
            )

            if response:

                writer.write(
                    (
                        json.dumps(response)
                        + "\n"
                    ).encode()
                )

                await writer.drain()

        except Exception as error:

            print(
                f"[Network] Error: {error}"
            )

        finally:

            writer.close()

            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def send_message(
        self,
        host,
        port,
        message,
        timeout=5
    ):

        writer = None

        try:

            reader, writer = await asyncio.wait_for(

                asyncio.open_connection(
                    host,
                    port
                ),

                timeout=timeout
            )

            writer.write(
                (
                    json.dumps(message)
                    + "\n"
                ).encode()
            )

            await writer.drain()

            data = await asyncio.wait_for(
                reader.readline(),
                timeout=timeout
            )

            if not data:
                return None

            return json.loads(
                data.decode()
            )

        except Exception:

            return None

        finally:

            if writer:

                writer.close()

                try:
                    await writer.wait_closed()
                except Exception:
                    pass

    async def stop(self):

        if self.server:

            self.server.close()

            await self.server.wait_closed()

            self.server = None