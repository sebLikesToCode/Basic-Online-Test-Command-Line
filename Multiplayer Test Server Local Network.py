import socket
import json
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5555))
server.listen()

size = 28
all_players = {}
last_seen = {}
player_names = {}
print("Server online. Waiting for players...")

while True:
    try:
        conn, addr = server.accept()
        raw_data = conn.recv(1024).decode()
        data = json.loads(raw_data)
        msg_type = data.get("type")

        if msg_type == "JOIN":
            # 1. Look for the first available Player number
            player_name = data.get("dis_name")
            existing_nums = [int(p.replace("Player", "")) for p in all_players.keys()]
            new_num = 1
            while new_num in existing_nums:
                new_num += 1

            p_id = f"Player{new_num}"
            all_players[p_id] = [5, 5]
            player_names[p_id] = data.get("dis_name")
            last_seen[p_id] = time.time()

            # 2. Send the ID string back
            conn.send(json.dumps({"id": p_id, "size": size}).encode())
            conn.close()

        else:

            p_id = data.get("id")
            action = data.get("action", "")

            if p_id in all_players:
                # 3. Create a 'hypothetical' new position
                pos = all_players[p_id]
                new_pos = list(pos)

                if "w" in action and new_pos[1] > 1: new_pos[1] -= 1
                if "s" in action and new_pos[1] < size - 2: new_pos[1] += 1
                if "a" in action and new_pos[0] > 1: new_pos[0] -= 1
                if "d" in action and new_pos[0] < size - 2: new_pos[0] += 1

                # 4. COLLISION CHECK
                collision = False
                for other_id, other_pos in all_players.items():
                    if other_id != p_id and other_pos == new_pos:
                        collision = True
                        break

                if not collision:
                    all_players[p_id] = new_pos

                last_seen[p_id] = time.time()

            packet = {
                "pos": all_players,
                "names": player_names
            }
            conn.send(json.dumps(packet).encode())

            conn.close()

    except Exception as e:
        print(f"Server Error: {e}")

    # Timeout cleanup
    now = time.time()
    for pid in list(all_players.keys()):
        if now - last_seen.get(pid, 0) > 5:
            del all_players[pid]
            del last_seen[pid]