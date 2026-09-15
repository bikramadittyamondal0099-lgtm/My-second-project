import hashlib
from collections import OrderedDict


class DHT:

    ID_BITS = 160

    K = 20

    def __init__(self, node):

        self.node = node

        self.buckets = {
            index: OrderedDict()

            for index in range(
                self.ID_BITS
            )
        }

    @staticmethod
    def generate_node_id(
        host,
        port
    ):

        value = (
            f"{host}:{port}"
        )

        return hashlib.sha1(
            value.encode()
        ).hexdigest()

    @staticmethod
    def xor_distance(
        id1,
        id2
    ):

        return (
            int(id1, 16)
            ^
            int(id2, 16)
        )

    def bucket_index(
        self,
        node_id
    ):

        distance = self.xor_distance(
            self.node.node_id,
            node_id
        )

        if distance == 0:
            return None

        return min(
            distance.bit_length() - 1,
            self.ID_BITS - 1
        )

    def add_peer(
        self,
        node_id,
        host,
        port,
        load=None
    ):

        if (
            not node_id
            or node_id == self.node.node_id
        ):
            return False

        index = self.bucket_index(
            node_id
        )

        if index is None:
            return False

        bucket = self.buckets[index]

        if node_id not in bucket:

            if len(bucket) >= self.K:

                bucket.popitem(
                    last=False
                )

            bucket[node_id] = {

                "node_id":
                    node_id,

                "host":
                    host,

                "port":
                    int(port),

                "load":
                    load or {
                        "cpu": 0,
                        "ram": 0,
                        "timestamp": 0
                    }
            }

        else:

            bucket[node_id]["host"] = host

            bucket[node_id]["port"] = int(port)

            if load:

                bucket[node_id]["load"] = load

            bucket.move_to_end(
                node_id
            )

        return True

    def remove_peer(
        self,
        node_id
    ):

        index = self.bucket_index(
            node_id
        )

        if index is not None:

            self.buckets[index].pop(
                node_id,
                None
            )

    def get_peer(
        self,
        node_id
    ):

        index = self.bucket_index(
            node_id
        )

        if index is None:
            return None

        return self.buckets[index].get(
            node_id
        )

    def peers(self):

        result = {}

        for bucket in self.buckets.values():

            result.update(
                bucket
            )

        return result

    def peer_count(self):

        return len(
            self.peers()
        )

    def closest(
        self,
        target_id=None,
        count=20
    ):

        if target_id is None:

            target_id = self.node.node_id

        peers = list(
            self.peers().values()
        )

        peers.sort(
            key=lambda peer:
                self.xor_distance(
                    target_id,
                    peer["node_id"]
                )
        )

        return peers[:count]