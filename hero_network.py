# -*- coding: utf-8 -*-

"""
HERO NETWORK — CLI Graph-Based Social Network

Features:
- Hero management (create, delete, login)
- Alliances (undirected graph)
- Messaging system
- Graph algorithms (BFS, connected components, analysis)

Data structures:
- dict  : stores heroes
- set   : stores alliances (O(1))
- deque : BFS traversal
"""

import hashlib
import os
import sys
from collections import deque

# ─────────────────────────────────────────────
# Global data
# ─────────────────────────────────────────────

heroes = {}
messages = []
current_user = None
message_id = 1


# ─────────────────────────────────────────────
# Utils
# ─────────────────────────────────────────────

def configure_utf8():
    if os.name == "nt":
        os.system("chcp 65001 > nul")
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        try:
            stream.reconfigure(encoding="utf-8")
        except:
            pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")


def normalize(name: str) -> str:
    return name.strip().lower()


def exists(name: str) -> bool:
    return name in heroes


def header(title=""):
    print("\n" + "-" * 50)
    if title:
        print(title)
        print("-" * 50)


def require_login():
    if current_user is None:
        print("No user logged in.")
        return None
    return current_user


# ─────────────────────────────────────────────
# Messaging
# ─────────────────────────────────────────────

def send_message(sender, receiver, text):
    global message_id

    sender = normalize(sender)
    receiver = normalize(receiver)
    text = text.strip()

    if not text:
        print("Empty message.")
        return False

    if not exists(receiver):
        print("User not found.")
        return False

    messages.append({
        "id": message_id,
        "from": sender,
        "to": receiver,
        "text": text
    })

    message_id += 1
    print("Message sent.")
    return True


def inbox(user):
    user = normalize(user)
    header(f"Inbox - {user}")

    user_messages = [m for m in messages if m["to"] == user]

    if not user_messages:
        print("No messages.")
        return

    for m in user_messages:
        print(f"{m['from']}: {m['text']}")


def conversation(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(b):
        print("User not found.")
        return

    header(f"Conversation: {a} <-> {b}")

    conv = [
        m for m in messages
        if (m["from"] == a and m["to"] == b)
        or (m["from"] == b and m["to"] == a)
    ]

    if not conv:
        print("No messages.")
        return

    for m in conv:
        print(f"{m['from']} -> {m['to']} : {m['text']}")


# ─────────────────────────────────────────────
# Hero management
# ─────────────────────────────────────────────

def add_hero(name, password):
    name = normalize(name)

    if exists(name):
        print("Hero already exists.")
        return False

    heroes[name] = {
        "password": hash_password(password),
        "allies": set()
    }

    print(f"Hero '{name}' created.")
    return True


def delete_hero(name, password):
    global current_user, messages

    name = normalize(name)

    if not exists(name):
        print("Hero not found.")
        return False

    if heroes[name]["password"] != hash_password(password):
        print("Wrong password.")
        return False

    for ally in heroes[name]["allies"]:
        heroes[ally]["allies"].discard(name)

    del heroes[name]

    messages = [
        m for m in messages
        if m["from"] != name and m["to"] != name
    ]

    if current_user == name:
        current_user = None

    print("Hero deleted.")
    return True


def login(name, password):
    global current_user

    name = normalize(name)

    if not exists(name) or heroes[name]["password"] != hash_password(password):
        print("Invalid credentials.")
        return False

    current_user = name
    print(f"Logged in as {name}")
    return True


def logout():
    global current_user

    if current_user is None:
        print("No user logged in.")
        return

    print(f"Logged out: {current_user}")
    current_user = None


# ─────────────────────────────────────────────
# Alliances (graph edges)
# ─────────────────────────────────────────────

def add_alliance(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b):
        print("User not found.")
        return False

    if a == b:
        print("Cannot ally with yourself.")
        return False

    if b in heroes[a]["allies"]:
        print("Already allied.")
        return False

    heroes[a]["allies"].add(b)
    heroes[b]["allies"].add(a)

    print("Alliance created.")
    return True


def remove_alliance(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b) or b not in heroes[a]["allies"]:
        print("Alliance not found.")
        return False

    heroes[a]["allies"].discard(b)
    heroes[b]["allies"].discard(a)

    print("Alliance removed.")
    return True


# ─────────────────────────────────────────────
# Graph algorithms
# ─────────────────────────────────────────────

def common_allies(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b):
        print("User not found.")
        return

    result = heroes[a]["allies"] & heroes[b]["allies"]

    header("Common Allies")

    if result:
        print(", ".join(sorted(result)))
    else:
        print("None")


def bfs(start):
    start = normalize(start)

    if not exists(start):
        print("User not found.")
        return

    visited = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for ally in heroes[current]["allies"]:
            if ally not in visited:
                visited.add(ally)
                queue.append(ally)

    visited.remove(start)

    header("Reachable Network")

    if visited:
        print(", ".join(sorted(visited)))
    else:
        print("No reachable allies.")


def connected_components():
    visited = set()
    components = []

    for hero in heroes:
        if hero in visited:
            continue

        queue = deque([hero])
        comp = set([hero])
        visited.add(hero)

        while queue:
            current = queue.popleft()
            for ally in heroes[current]["allies"]:
                if ally not in visited:
                    visited.add(ally)
                    comp.add(ally)
                    queue.append(ally)

        components.append(comp)

    return components


def analyze_network():
    header("Network Analysis")

    if not heroes:
        print("Empty network.")
        return

    degrees = {h: len(v["allies"]) for h, v in heroes.items()}

    n = len(degrees)
    e = sum(degrees.values()) // 2

    avg = sum(degrees.values()) / n if n else 0
    density = (2 * e) / (n * (n - 1)) if n > 1 else 0

    print(f"Heroes     : {n}")
    print(f"Alliances  : {e}")
    print(f"Avg degree : {avg:.2f}")
    print(f"Density    : {density:.3f}")
    print(f"Components : {len(connected_components())}")


# ─────────────────────────────────────────────
# Menu
# ─────────────────────────────────────────────

def menu():
    while True:
        clear()
        print("""
HERO NETWORK CLI

1. Create hero
2. Delete hero
3. Login
4. Add alliance
5. Remove alliance
6. Common allies
7. BFS
8. Analyze network

M. Send message
B. Inbox
C. Conversation
X. Logout
Q. Quit
""")

        print(f"Current user: {current_user if current_user else 'None'}")

        choice = input("Choice: ").strip().upper()

        if choice == "Q":
            break

        elif choice == "1":
            add_hero(input("Name: "), input("Password: "))

        elif choice == "2":
            delete_hero(input("Name: "), input("Password: "))

        elif choice == "3":
            login(input("Name: "), input("Password: "))

        elif choice == "4":
            add_alliance(input("Hero 1: "), input("Hero 2: "))

        elif choice == "5":
            remove_alliance(input("Hero 1: "), input("Hero 2: "))

        elif choice == "6":
            common_allies(input("Hero 1: "), input("Hero 2: "))

        elif choice == "7":
            bfs(input("Start hero: "))

        elif choice == "8":
            analyze_network()

        elif choice == "M":
            user = require_login()
            if user:
                send_message(user, input("To: "), input("Message: "))

        elif choice == "B":
            user = require_login()
            if user:
                inbox(user)

        elif choice == "C":
            user = require_login()
            if user:
                conversation(user, input("With: "))

        elif choice == "X":
            logout()

        else:
            print("Invalid choice.")

        pause()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    configure_utf8()
    menu()# -*- coding: utf-8 -*-

"""
HERO NETWORK — CLI Graph-Based Social Network

Features:
- Hero management (create, delete, login)
- Alliances (undirected graph)
- Messaging system
- Graph algorithms (BFS, connected components, analysis)

Data structures:
- dict  : stores heroes
- set   : stores alliances (O(1))
- deque : BFS traversal
"""

import hashlib
import os
import sys
from collections import deque

# ─────────────────────────────────────────────
# Global data
# ─────────────────────────────────────────────

heroes = {}
messages = []
current_user = None
message_id = 1


# ─────────────────────────────────────────────
# Utils
# ─────────────────────────────────────────────

def configure_utf8():
    if os.name == "nt":
        os.system("chcp 65001 > nul")
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        try:
            stream.reconfigure(encoding="utf-8")
        except:
            pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")


def normalize(name: str) -> str:
    return name.strip().lower()


def exists(name: str) -> bool:
    return name in heroes


def header(title=""):
    print("\n" + "-" * 50)
    if title:
        print(title)
        print("-" * 50)


def require_login():
    if current_user is None:
        print("No user logged in.")
        return None
    return current_user


# ─────────────────────────────────────────────
# Messaging
# ─────────────────────────────────────────────

def send_message(sender, receiver, text):
    global message_id

    sender = normalize(sender)
    receiver = normalize(receiver)
    text = text.strip()

    if not text:
        print("Empty message.")
        return False

    if not exists(receiver):
        print("User not found.")
        return False

    messages.append({
        "id": message_id,
        "from": sender,
        "to": receiver,
        "text": text
    })

    message_id += 1
    print("Message sent.")
    return True


def inbox(user):
    user = normalize(user)
    header(f"Inbox - {user}")

    user_messages = [m for m in messages if m["to"] == user]

    if not user_messages:
        print("No messages.")
        return

    for m in user_messages:
        print(f"{m['from']}: {m['text']}")


def conversation(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(b):
        print("User not found.")
        return

    header(f"Conversation: {a} <-> {b}")

    conv = [
        m for m in messages
        if (m["from"] == a and m["to"] == b)
        or (m["from"] == b and m["to"] == a)
    ]

    if not conv:
        print("No messages.")
        return

    for m in conv:
        print(f"{m['from']} -> {m['to']} : {m['text']}")


# ─────────────────────────────────────────────
# Hero management
# ─────────────────────────────────────────────

def add_hero(name, password):
    name = normalize(name)

    if exists(name):
        print("Hero already exists.")
        return False

    heroes[name] = {
        "password": hash_password(password),
        "allies": set()
    }

    print(f"Hero '{name}' created.")
    return True


def delete_hero(name, password):
    global current_user, messages

    name = normalize(name)

    if not exists(name):
        print("Hero not found.")
        return False

    if heroes[name]["password"] != hash_password(password):
        print("Wrong password.")
        return False

    for ally in heroes[name]["allies"]:
        heroes[ally]["allies"].discard(name)

    del heroes[name]

    messages = [
        m for m in messages
        if m["from"] != name and m["to"] != name
    ]

    if current_user == name:
        current_user = None

    print("Hero deleted.")
    return True


def login(name, password):
    global current_user

    name = normalize(name)

    if not exists(name) or heroes[name]["password"] != hash_password(password):
        print("Invalid credentials.")
        return False

    current_user = name
    print(f"Logged in as {name}")
    return True


def logout():
    global current_user

    if current_user is None:
        print("No user logged in.")
        return

    print(f"Logged out: {current_user}")
    current_user = None


# ─────────────────────────────────────────────
# Alliances (graph edges)
# ─────────────────────────────────────────────

def add_alliance(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b):
        print("User not found.")
        return False

    if a == b:
        print("Cannot ally with yourself.")
        return False

    if b in heroes[a]["allies"]:
        print("Already allied.")
        return False

    heroes[a]["allies"].add(b)
    heroes[b]["allies"].add(a)

    print("Alliance created.")
    return True


def remove_alliance(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b) or b not in heroes[a]["allies"]:
        print("Alliance not found.")
        return False

    heroes[a]["allies"].discard(b)
    heroes[b]["allies"].discard(a)

    print("Alliance removed.")
    return True


# ─────────────────────────────────────────────
# Graph algorithms
# ─────────────────────────────────────────────

def common_allies(a, b):
    a, b = normalize(a), normalize(b)

    if not exists(a) or not exists(b):
        print("User not found.")
        return

    result = heroes[a]["allies"] & heroes[b]["allies"]

    header("Common Allies")

    if result:
        print(", ".join(sorted(result)))
    else:
        print("None")


def bfs(start):
    start = normalize(start)

    if not exists(start):
        print("User not found.")
        return

    visited = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for ally in heroes[current]["allies"]:
            if ally not in visited:
                visited.add(ally)
                queue.append(ally)

    visited.remove(start)

    header("Reachable Network")

    if visited:
        print(", ".join(sorted(visited)))
    else:
        print("No reachable allies.")


def connected_components():
    visited = set()
    components = []

    for hero in heroes:
        if hero in visited:
            continue

        queue = deque([hero])
        comp = set([hero])
        visited.add(hero)

        while queue:
            current = queue.popleft()
            for ally in heroes[current]["allies"]:
                if ally not in visited:
                    visited.add(ally)
                    comp.add(ally)
                    queue.append(ally)

        components.append(comp)

    return components


def analyze_network():
    header("Network Analysis")

    if not heroes:
        print("Empty network.")
        return

    degrees = {h: len(v["allies"]) for h, v in heroes.items()}

    n = len(degrees)
    e = sum(degrees.values()) // 2

    avg = sum(degrees.values()) / n if n else 0
    density = (2 * e) / (n * (n - 1)) if n > 1 else 0

    print(f"Heroes     : {n}")
    print(f"Alliances  : {e}")
    print(f"Avg degree : {avg:.2f}")
    print(f"Density    : {density:.3f}")
    print(f"Components : {len(connected_components())}")


# ─────────────────────────────────────────────
# Menu
# ─────────────────────────────────────────────

def menu():
    while True:
        clear()
        print("""
HERO NETWORK CLI

1. Create hero
2. Delete hero
3. Login
4. Add alliance
5. Remove alliance
6. Common allies
7. BFS
8. Analyze network

M. Send message
B. Inbox
C. Conversation
X. Logout
Q. Quit
""")

        print(f"Current user: {current_user if current_user else 'None'}")

        choice = input("Choice: ").strip().upper()

        if choice == "Q":
            break

        elif choice == "1":
            add_hero(input("Name: "), input("Password: "))

        elif choice == "2":
            delete_hero(input("Name: "), input("Password: "))

        elif choice == "3":
            login(input("Name: "), input("Password: "))

        elif choice == "4":
            add_alliance(input("Hero 1: "), input("Hero 2: "))

        elif choice == "5":
            remove_alliance(input("Hero 1: "), input("Hero 2: "))

        elif choice == "6":
            common_allies(input("Hero 1: "), input("Hero 2: "))

        elif choice == "7":
            bfs(input("Start hero: "))

        elif choice == "8":
            analyze_network()

        elif choice == "M":
            user = require_login()
            if user:
                send_message(user, input("To: "), input("Message: "))

        elif choice == "B":
            user = require_login()
            if user:
                inbox(user)

        elif choice == "C":
            user = require_login()
            if user:
                conversation(user, input("With: "))

        elif choice == "X":
            logout()

        else:
            print("Invalid choice.")

        pause()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    configure_utf8()
    menu()