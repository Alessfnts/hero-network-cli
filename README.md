# Hero Network CLI

A command-line application to manage a network of heroes, alliances, and messaging.

## Features

- Create and delete heroes (with secure password hashing using SHA-256)
- Authentication system (login/logout)
- Create and remove alliances between heroes
- View hero profiles and the global network
- Messaging system (send messages, inbox, conversations)
- Graph algorithms:
  - Breadth-First Search (BFS) for network reachability
  - Common allies detection
  - Connected components
  - Network analysis (density, degree, etc.)
- Demo mode with preloaded data

## Data Structures Used

- `dict`: stores heroes and their associated data
- `set`: ensures unique alliances with O(1) operations
- `deque`: used for efficient BFS traversal

## Algorithms

- Breadth-First Search (BFS)
- Graph connectivity analysis
- Set intersection for common allies

## How to Run

```bash
python hero_network.py
