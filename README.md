# MeshWeaver: Zero-Dependency P2P Async Task Broker

## About the Project

MeshWeaver is a decentralized P2P task broker built with Python. It allows multiple nodes to discover each other, share system load, distribute tasks, and execute them remotely without a central server.

## 4 Weeks of Work

### Week 1
- Built asynchronous TCP communication using `asyncio`.
- Implemented task serialization and remote execution.
- Added result transfer between nodes.

### Week 2
- Implemented a Kademlia-style DHT.
- Added peer discovery and XOR-based node IDs.
- Implemented Gossip Protocol for CPU/RAM sharing.

### Week 3
- Added load-based task routing.
- Implemented heartbeat monitoring.
- Added peer failure detection and task re-routing.

### Week 4
- Added HMAC-SHA256 message security.
- Built a Tkinter graphical dashboard.
- Added CPU/RAM monitoring, peer list, task submission, results, and live logs.

## What I Learned

- Python `asyncio` and TCP networking
- P2P and distributed-system concepts
- DHT and peer discovery
- Gossip and heartbeat protocols
- Task serialization and remote execution
- Load-based task scheduling
- Fault tolerance and security
- Tkinter GUI development
- Connecting GUI with an asynchronous backend

## Conclusion

MeshWeaver successfully demonstrates a decentralized task-broker system with peer discovery, remote task execution, load-based routing, fault detection, security, and a graphical dashboard. The project gave me practical experience in **distributed systems, networking, asynchronous programming, and edge-computing concepts**.
