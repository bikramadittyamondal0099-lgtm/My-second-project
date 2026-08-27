# MeshWeaver

MeshWeaver is a decentralized peer-to-peer asynchronous task broker built with Python.

The project is designed for distributed and edge-computing environments where a central task broker is undesirable.

## Week 1

Week 1 implements the basic asynchronous networking layer.

Features:

- Async TCP communication
- Independent Python nodes
- PING/PONG communication
- Peer registration
- Python function serialization
- Remote task execution
- Result transmission

## Week 2

Week 2 introduces decentralized peer discovery and system-state sharing.

Features:

- SHA-256 node identifiers
- Lightweight Kademlia-style DHT
- Dynamic peer discovery
- Bootstrap nodes
- Gossip protocol
- CPU load broadcasting
- Distributed peer state

## Running MeshWeaver

Start the first node:

```bash
python main.py 5001
