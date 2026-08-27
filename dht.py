import hashlib
class DHT:
    def __init__(self, node):
        self.node = node
        self.routing_table = {}
    def generate_node_id(self, host, port):
        value = f"{host}:{port}"
        return hashlib.sha256(value.encode()).hexdigest()
    def add_peer(self, node_id, host, port):
        if node_id != self.node.node_id:
            self.routing_table[node_id] = {
                "host": host,
                "port": port
            }
    def remove_peer(self, node_id):
        self.routing_table.pop(node_id, None)
    def find_closest_nodes(self, count=3):
        peers = list(self.routing_table.items())
        peers.sort(
            key=lambda item: int(item[0], 16)
        )
        return peers[:count]
    def get_peers(self):
        return self.routing_table
