import socket
import tkinter as tk
import pickle
import configparser
import random
from PowerUp import PowerUp
from Player import Player

config = configparser.ConfigParser()
config.read('config.ini')
board_width = config.getint('Board', 'Width')
board_height = config.getint('Board', 'Height')
powerups_color = config.get('Powerups', 'color')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 12345))
root = tk.Tk()
canvas = tk.Canvas(root, width=board_width, height=board_height)
canvas.pack()
players_to_dots = {}  # maps players to their dots
powerups_to_powerups_objects = {}  # numbers to powerups objects


def grow_dot(player: Player, grow_by=3):
    for p in players_to_dots:
        if p.address == player.address:
            dot_id = players_to_dots[p]
            x1, y1, x2, y2 = canvas.coords(dot_id)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            canvas.delete(dot_id)
            new_dot_id = canvas.create_oval(center_x - grow_by / 2 - (x2 - x1) / 2,
                                            center_y - grow_by / 2 - (y2 - y1) / 2,
                                            center_x + grow_by / 2 + (x2 - x1) / 2,
                                            center_y + grow_by / 2 + (y2 - y1) / 2,
                                            fill=player.color)
            players_to_dots[p] = new_dot_id
            player.size += 1
            return new_dot_id
    else:
        raise Exception('grow_dot : dot not found')


def CreatePowerUps():
    # Determine the number of powerups
    num_powerups = random.randint(4, 8)
    # Create the powerups
    for _ in range(num_powerups):
        # Randomly position the powerup
        x1 = random.randint(0, 800)
        y1 = random.randint(0, 600)
        x2 = x1 + 10
        y2 = y1
        x3 = x1 + 5
        y3 = y1 - 10
        powerup = canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill=powerups_color)
        powerups_object = PowerUp(x1, x2, x3, y1, y2, y3, powerups_color)
        powerups_to_powerups_objects[powerup] = [powerups_object]


def SendPowerUps(address):
    for powerup in powerups_to_powerups_objects:
        message = pickle.dumps(('PowerUps', (powerup, powerups_to_powerups_objects[powerup])))
        server_socket.sendto(message, address)


def FindPlayerWithAddress(address):
    for player in players_to_dots:
        if player.address == address:
            return player
    print("error")


def SendOtherPlayerYouConsumePowerUp(powerup, curr_player):
    for player in players_to_dots:
        if player.address != curr_player.address:
            message = pickle.dumps(
                ('Other Consume PowerUps', (curr_player, (powerup, powerups_to_powerups_objects[powerup]))))
            server_socket.sendto(message, player.address)


def HandleEncounterPolygon(powerup, player: Player):
    message = pickle.dumps(('You Consume PowerUps', (powerup, powerups_to_powerups_objects[powerup])))
    server_socket.sendto(message, player.address)
    canvas.delete(powerup)
    grow_dot(player)
    SendOtherPlayerYouConsumePowerUp(powerup, player)
    powerups_to_powerups_objects.pop(powerup)


def GetDotSize(dot_id):
    x1, y1, x2, y2 = canvas.coords(dot_id)
    # Since it's a circle, the diameter can be calculated using either the x or y coordinates
    diameter = x2 - x1
    return diameter


def SendOtherPlayersYouLose(died_player: Player):
    for player in players_to_dots:
        if player.address != died_player.address:
            message = pickle.dumps(('Player died', died_player))
            server_socket.sendto(message, player.address)


def SendYouLose(died_player: Player):
    message = pickle.dumps(('You Lose', died_player))
    server_socket.sendto(message, died_player.address)
    player_dot = players_to_dots.pop(died_player)
    canvas.delete(player_dot)
    SendOtherPlayersYouLose(died_player)


def SendPlayerDied(kill_player: Player, died_player: Player):
    for player in players_to_dots:
        if player.address != kill_player and player.address != died_player:
            message = pickle.dumps(('Player died', died_player))
            server_socket.sendto(message, player.address)


def SendPlayerGrow(kill_player: Player, died_player: Player):
    for player in players_to_dots:
        if player.address != kill_player and player.address != died_player:
            message = pickle.dumps(('Player Grow', kill_player))
            server_socket.sendto(message, player.address)


def SendOtherPlayerYouKillAPlayer(kill_player: Player, died_player: Player):
    # send player grow because kill
    SendPlayerGrow(kill_player, died_player)
    # send player died
    SendPlayerDied(kill_player, died_player)


def SendYouWin(kill_player: Player, died_player: Player):
    grow_dot(kill_player)
    message = pickle.dumps(('Kill Player', died_player))
    server_socket.sendto(message, kill_player.address)
    SendYouLose(died_player)
    for p in players_to_dots:
        if p.address != died_player.address and p.address != kill_player.address:
            SendOtherPlayerYouKillAPlayer(kill_player, died_player)


def HandleEncounterOval(player, other_player_dot):
    player_dot = players_to_dots[player]
    player_dot_size = GetDotSize(player_dot)
    other_player_dot_size = GetDotSize(other_player_dot)
    if player_dot_size > other_player_dot_size:
        for other_player, other_dot in dict(players_to_dots).items():
            if other_dot == other_player_dot:
                SendYouWin(player, other_player)
    if other_player_dot_size > player_dot_size:
        for other_player, other_dot in dict(players_to_dots).items():
            if other_dot == other_player_dot:
                SendYouWin(other_player, player)


def CheckIfEncounterAnything(player):
    player_dot = players_to_dots[player]
    dot_coords = canvas.coords(player_dot)
    items_overlapping = canvas.find_overlapping(*dot_coords)  # unpack the list to four arguments
    for thing in items_overlapping:
        if thing != player_dot:
            item_type = canvas.type(thing)
            if item_type == 'polygon':  # triangle - powerup
                HandleEncounterPolygon(thing, player)
            if item_type == 'oval':  # circle - other player
                HandleEncounterOval(player, thing)


def UpdateForMove(current_player: Player):
    print(f"UpdateForMove - player  - {current_player}")
    for player in players_to_dots:
        if player.address != current_player.address:
            message = 'UpdateMove: other player'
            combine_message = pickle.dumps((message, current_player))
            server_socket.sendto(combine_message, player.address)


def move(message, player):
    x, y = map(float, message[1:])
    x = int(x)
    y = int(y)
    player.position_x = x
    player.position_y = y
    canvas.moveto(players_to_dots[player], x, y)
    CheckIfEncounterAnything(player)
    UpdateForMove(player)


actions_map = {'move': move}


def SendAllOtherPlayers(address):
    for player in players_to_dots:
        message = 'Get: other player'
        combine_message = pickle.dumps((message, player))
        server_socket.sendto(combine_message, address)


def SendSavedPlayer(player_name):
    print(player_name)


def CreateANewPlayer(data, address):
    stats = data.split(',')
    player_name = stats[0]
    x = stats[1]
    y = stats[2]
    size = int(stats[3])
    color = stats[4]
    new_player = Player(address, player_name, x, y, size, color)

    new_player_dot = canvas.create_oval(50, 50, 60, 60, fill=color)
    canvas.moveto(new_player_dot, x, y)
    print(f"new_player: {new_player}")
    message = f"successfully connect to server your address is ,{new_player.address}"
    combine_message = pickle.dumps((message, new_player))
    send_to = new_player.address
    server_socket.sendto(combine_message, send_to)
    SendPowerUps(send_to)
    SendAllOtherPlayers(address)
    players_to_dots[new_player] = new_player_dot
    return new_player


def UpdateConnection(new_player):
    message = 'Update: a new player connected'
    combine_message = pickle.dumps((message, new_player))
    for player in players_to_dots:
        if player.address != new_player.address:
            send_to = player.address
            server_socket.sendto(combine_message, send_to)
            print(f"send message {combine_message} to {send_to}")


def main():
    print('server start')
    CreatePowerUps()
    while True:
        data, address = server_socket.recvfrom(1024)
        print("Received from:", address)
        if not data:
            break
        all_addresses = [player.address for player in players_to_dots]
        if address not in all_addresses:
            new_player = CreateANewPlayer(data.decode('utf-8'), address)
            UpdateConnection(new_player)

        message = data.decode('utf-8').split(',')
        command = message[0]
        player = FindPlayerWithAddress(address)
        if command in actions_map:
            actions_map[command](message, player)

    print("Server closed")


if __name__ == "__main__":
    main()
