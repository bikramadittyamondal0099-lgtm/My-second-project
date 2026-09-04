import hashlib


class DHT:
    """
    Lightweight Kademlia-style Distributed Hash Table.

    Week 2 features:

    - SHA-1 node IDs
    - XOR distance
    - 160 routing buckets
    - K value of 20
    - Dynamic peer discovery
    - Closest-node lookup
    """

    ID_BITS = 160
    K = 20

    def __init__(self, node):

        self.node = node

        # 160 Kademlia-style buckets
        self.routing_table = {
            i: {}
            for i in range(self.ID_BITS)
        }

    # --------------------------------------------------
    # NODE ID
    # --------------------------------------------------

    @staticmethod
    def generate_node_id(host, port):

        value = f"{host}:{port}"

        return hashlib.sha1(
            value.encode()
        ).hexdigest()

    # --------------------------------------------------
    # XOR DISTANCE
    # --------------------------------------------------

    @staticmethod
    def xor_distance(node_a, node_b):

        return (
            int(node_a, 16)
            ^ int(node_b, 16)
        )

    # --------------------------------------------------
    # BUCKET INDEX
    # --------------------------------------------------

    def get_bucket_index(self, node_id):

        distance = self.xor_distance(
            self.node.node_id,
            node_id
        )

        if distance == 0:
            return None

        index = distance.bit_length() - 1

        return min(
            index,
            self.ID_BITS - 1
        )

    # --------------------------------------------------
    # ADD PEER
    # --------------------------------------------------

    def add_peer(
        self,
        node_id,
        host,
        port,
        load=None
    ):

        if not self.node.node_id:
            return False

        if node_id == self.node.node_id:
            return False

        bucket_index = self.get_bucket_index(
            node_id
        )

        if bucket_index is None:
            return False

        bucket = self.routing_table[
            bucket_index
        ]

        if node_id in bucket:

            bucket[node_id]["host"] = host
            bucket[node_id]["port"] = port

            if load is not None:
                bucket[node_id]["load"] = load

            return True

        # Kademlia K value
        if len(bucket) >= self.K:

            # Simple educational replacement policy
            oldest_peer = next(
                iter(bucket)
            )

            del bucket[oldest_peer]

        bucket[node_id] = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "load": load or {
                "cpu": 0,
                "ram": 0,
                "timestamp": 0
            }
        }

        return True

    # --------------------------------------------------
    # REMOVE PEER
    # --------------------------------------------------

    def remove_peer(self, node_id):

        bucket_index = self.get_bucket_index(
            node_id
        )

        if bucket_index is None:
            return

        self.routing_table[
            bucket_index
        ].pop(
            node_id,
            None
        )

    # --------------------------------------------------
    # GET SINGLE PEER
    # --------------------------------------------------

    def get_peer(self, node_id):

        for bucket in self.routing_table.values():

            if node_id in bucket:
                return bucket[node_id]

        return None

    # --------------------------------------------------
    # UPDATE LOAD
    # --------------------------------------------------

    def update_peer_load(
        self,
        node_id,
        load
    ):

        peer = self.get_peer(node_id)

        if peer:

            peer["load"] = load

            return True

        return False

    # --------------------------------------------------
    # GET ALL PEERS
    # --------------------------------------------------

    def get_peers(self):

        peers = {}

        for bucket in self.routing_table.values():

            peers.update(bucket)

        return peers

    # --------------------------------------------------
    # FIND CLOSEST NODES
    # --------------------------------------------------

    def find_closest_nodes(
        self,
        target_id=None,
        count=3
    ):

        if target_id is None:
            target_id = self.node.node_id

        peers = list(
            self.get_peers().values()
        )

        peers.sort(
            key=lambda peer:
                self.xor_distance(
                    target_id,
                    peer["node_id"]
                )
        )

        return peers[:count]

    # --------------------------------------------------
    # ROUTING TABLE INFO
    # --------------------------------------------------

    def bucket_summary(self):

        return {
            bucket_id: len(peers)
            for bucket_id, peers
            in self.routing_table.items()
            if peers
        }

    # --------------------------------------------------
    # TOTAL PEERS
    # --------------------------------------------------

    def peer_count(self):

        return len(
            self.get_peers()
        )
