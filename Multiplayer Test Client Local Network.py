from logging import exception

import keyboard
import time
import json
import socket
dis_name = input("Choose your name: ")
# --- Handshake ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5555))
client.send(json.dumps({"type": "JOIN", "dis_name": dis_name}).encode())
startup_data = json.loads(client.recv(1024).decode())
my_id = startup_data["id"]  # This is now "Player1", "Player2", etc.
size = startup_data["size"]
client.close()

wall = "██"
space = "  "
plr_XY = [5, 5]
players = {}


def print_board(player_dict, my_id, names_lookup):
    others = sorted([n for n in player_dict.keys() if n != my_id])
    buffer = []

    # 1. Start at top-left and hide cursor
    buffer.append("\033[H\033[?25l")
    buffer.append(wall * size + f"  Player: {names_lookup.get(my_id, '...')}\n")

    # 2. Draw the grid
    for y in range(1, size - 1):
        line = [wall]  # Left wall
        for x in range(1, size - 1):
            char_to_print = space

            # Check for players at this tile
            for p_id, pos in player_dict.items():
                if pos == [x, y]:
                    if p_id == my_id:
                        char_to_print = "██"
                    else:
                        rank = others.index(p_id)
                        colors = ["\033[31m", "\033[32m", "\033[33m", "\033[36m"]
                        color = colors[rank] if rank < len(colors) else "\033[37m"
                        char_to_print = f"{color}██\033[0m"
                    break

                # NAME LOGIC: Check if this tile should contain a name letter
                # We check the tile directly ABOVE the player (pos[1]-1)
                elif pos[0] <= x < pos[0] + 2 and y == pos[1] - 1:
                    name = names_lookup.get(p_id, "Guest")
                    # Since each tile is 2 chars wide (space is "  "),
                    # we grab 2 chars of the name per tile
                    offset = (x - pos[0]) * 2
                    name_part = name[offset:offset + 2]
                    # Pad with spaces if the name is short
                    if len(name_part) < 2: name_part += " "
                    char_to_print = f"\033[1;30m{name_part}\033[0m"
                    break

            line.append(char_to_print)
        line.append(wall + "\n")  # Right wall
        buffer.append("".join(line))

    buffer.append(wall * size + "\n")

    # 3. Final Reset (No more Step 3 absolute positioning!)
    buffer.append(f"\033[{size + 2};1H")
    print("".join(buffer), end="", flush=True)
def move_plr():
    global plr_XY
    act = ""
    if keyboard.is_pressed("w"):
        act += "w"
       # if plr_XY[1] > 1: plr_XY[1] -= 1
    if keyboard.is_pressed("s"):
        act += "s"
      #  if plr_XY[1] < size - 2: plr_XY[1] += 1
    if keyboard.is_pressed("a"):
        act += "a"
       # if plr_XY[0] > 1: plr_XY[0] -= 1
    if keyboard.is_pressed("d"):
        act += "d"
        #if plr_XY[0] < size - 2: plr_XY[0] += 1
    return act


# --- Initialize variables before the loop ---
players = {}
names_lookup = {}

while True:
    # Use the 'l' (lower case L) to hide cursor
    print("\033[?25l", end="")

    action = move_plr()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)  # Don't hang forever if the server is slow
        s.connect(('127.0.0.1', 5555))
        s.send(json.dumps({"id": my_id, "action": action}).encode())

        resp = s.recv(4096).decode()  # Increased buffer size for many players

        if resp:
            data = json.loads(resp)
            # Update our local storage with server data
            players = data.get("pos", {})
            names_lookup = data.get("names", {})

            if my_id in players:
                plr_XY = players[my_id]
        s.close()
    except Exception as e:
        excepted = e # If the server fails, we keep the last known 'players' and 'names_lookup'
        pass

    # Now print_board will always have a dict (even if empty)
    print_board(players, my_id, names_lookup)
    time.sleep(0.05)