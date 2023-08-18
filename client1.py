import random
import threading
import time
import tkinter
import tkinter as tk
import socket
import pickle
import configparser
from tkinter import messagebox
from tkinter import simpledialog, colorchooser
from LoginWindow import LoginWindow
from itertools import cycle

from PowerUp import PowerUp
from Player import Player
from SpeedBoostPowerUp import SpeedBoostPowerUp

config = configparser.ConfigParser()
config.read('config.ini')

board_width = config.getint('Board', 'Width')
board_height = config.getint('Board', 'Height')
powerups_color = config.get('Powerups', 'color')
fences_color = config.get('Fences', 'color')
fences_width = config.getfloat('Fences', 'width')
speed_boost_PowerUp_color_inside = config.get('SpeedBoostPowerUp', 'color_inside')
speed_boost_PowerUp_color_outside = config.get('SpeedBoostPowerUp', 'color_outside')

root: tkinter.Tk
canvas: tkinter.Canvas

my_dot = None  # my dot id
my_color = None  # my dot color
my_name = None  # chosen name
my_speed = 1

players_to_dots = {}  # maps players to their dots - only others
powerups_to_powerups_objects = {}  # numbers to powerups objects
speed_powerups_to_speed_powerups_objects = {}  # numbers to speed powerups objects
server_powerup_to_player_powerup = {}  # int to int
fences_to_fences_object = {}  # number to fence objects
server_fences_to_player_fences = {}  # int to int
speed_boost_to_speed_boost_object = {}  # number to speed_boost objects
server_speed_boost_to_player_speed_boost = {}  # int to int
flame_pos_x: int = 0
flame_pos_y: int = 0
flame_cycle = None


def move_dot(client_socket, event, player_dot, server_address):
    global my_speed
    x, y = canvas.coords(player_dot)[:2]  # Get current position
    dx, dy = 0, 0
    if event.keysym == 'Up':
        dy = (-10 * my_speed)
    elif event.keysym == 'Down':
        dy = (10 * my_speed)
    elif event.keysym == 'Left':
        dx = (-10 * my_speed)
    elif event.keysym == 'Right':
        dx = (10 * my_speed)
    x += dx
    y += dy
    message = f"move,{x},{y}"
    client_socket.sendto(message.encode('utf-8'), server_address)
    canvas.move(player_dot, dx, dy)  # Update position


def AssemblePowerUps(powerup_tuple):
    print(f"powerup = {powerup_tuple}")
    server_powerup = powerup_tuple[0]
    powerup_object = powerup_tuple[1][0]
    player_powerup = canvas.create_polygon(powerup_object.x1, powerup_object.y1, powerup_object.x2, powerup_object.y2,
                                           powerup_object.x3, powerup_object.y3, fill=powerups_color)
    server_powerup_to_player_powerup[server_powerup] = player_powerup


def AssembleFences(fences_tuple):
    print(f"fences_tuple = {fences_tuple}")
    server_fences = fences_tuple[0]
    fences_object = fences_tuple[1][0]
    player_fences = canvas.create_line(fences_object.x1, fences_object.y1, fences_object.x2, fences_object.y2,
                                       fill=fences_color, width=fences_width)
    server_fences_to_player_fences[server_fences] = player_fences


def AssembleSpeedBoost(speed_boost_tuple):
    print(speed_boost_tuple)
    server_speed_boost = speed_boost_tuple[0]
    speed_boost_object = speed_boost_tuple[1][0]
    x = speed_boost_object.x
    y = speed_boost_object.y
    speed_boost_object = SpeedBoostPowerUp(x, y, speed_boost_PowerUp_color_inside, speed_boost_PowerUp_color_outside)
    points = speed_boost_object.get_points_for_polygon()
    player_speed_boost = canvas.create_polygon(points, fill=speed_boost_object.color_inside,
                                               outline=speed_boost_object.color_outside)
    server_speed_boost_to_player_speed_boost[server_speed_boost] = player_speed_boost


def CreateNewOtherPlayer(other_player: Player):
    other_player_dot = canvas.create_oval(50, 50, 60, 60, fill=other_player.color)
    canvas.moveto(other_player_dot, other_player.position_x, other_player.position_y)
    players_to_dots[other_player] = other_player_dot


def GetOtherPlayer(other_player: Player):
    other_player_dot = canvas.create_oval(50, 50, 60, 60, fill=other_player.color)
    canvas.moveto(other_player_dot, other_player.position_x, other_player.position_y)
    for i in range(other_player.size):
        other_player_dot = grow_dot(other_player_dot, other_player.color)
    players_to_dots[other_player] = other_player_dot


def UpdateMoveOtherPlayer(other_player: Player):
    print(f"UpdateMoveOtherPlayer = new player = {other_player}")
    for player in players_to_dots:
        if player.address == other_player.address:
            player.position_x = other_player.position_x
            player.position_y = other_player.position_y
            dot_to_move = players_to_dots[player]
            x, y = canvas.coords(dot_to_move)[:2]  # get current position
            dx = other_player.position_x - int(x)
            dy = other_player.position_y - int(y)
            canvas.move(dot_to_move, dx, dy)
            break


def grow_dot(dot_id, color=my_color, grow_by=3):  ## change to get only player
    x1, y1, x2, y2 = canvas.coords(dot_id)
    print(x1, y1, x2, y2)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    canvas.delete(dot_id)
    for key, value in dict(players_to_dots).items():
        if value == dot_id:
            del players_to_dots[key]
    new_dot_id = canvas.create_oval(center_x - grow_by / 2 - (x2 - x1) / 2, center_y - grow_by / 2 - (y2 - y1) / 2,
                                    center_x + grow_by / 2 + (x2 - x1) / 2, center_y + grow_by / 2 + (y2 - y1) / 2,
                                    fill=color)
    x11, y11, x21, y21 = canvas.coords(new_dot_id)
    print(x11, y11, x21, y21)
    root.update()
    return new_dot_id


def YouConsumePowerUp(powerup_tuple):
    global my_dot
    print(powerup_tuple)
    print(canvas.find_all())
    server_powerup = powerup_tuple[0]
    powerup_object = powerup_tuple[1][0]
    player_power_up = server_powerup_to_player_powerup[server_powerup]
    canvas.delete(player_power_up)
    my_dot = grow_dot(my_dot, my_color)


def OtherConsumePowerUp(other_player_powerup_tuple):
    print(other_player_powerup_tuple)
    other_player = other_player_powerup_tuple[0]
    server_powerup = other_player_powerup_tuple[1][0]
    powerup_object = other_player_powerup_tuple[1][1][0]
    powerup = server_powerup_to_player_powerup[server_powerup]
    canvas.delete(powerup)
    for player in players_to_dots:
        if player.address == other_player.address:
            players_to_dots[other_player] = grow_dot(players_to_dots[player], other_player.color)
            break


def IncreaseSpeed():
    global my_speed
    my_speed += 0.75


def animate_explosion(x, y, explosion_cycle):
    try:
        frame = next(explosion_cycle)
        explosion = canvas.create_image(x, y, image=frame)
        root.after(35, lambda: canvas.delete(explosion))
        root.after(35, animate_explosion, x, y, explosion_cycle)
    except StopIteration:
        # Once all frames have been shown, stop the animation.
        pass


def animate_lighting(x, y, lighting_iter):
    try:
        frame = next(lighting_iter)
        explosion = canvas.create_image(x, y, image=frame)
        root.after(30, lambda: canvas.delete(explosion))
        root.after(30, animate_lighting, x, y, lighting_iter)
    except StopIteration:
        # Once all frames have been shown, stop the animation.
        pass


def YouConsumeSpeedPowerUp(speed_powerup_tuple):
    global my_dot
    print(speed_powerup_tuple)
    print(canvas.find_all())
    server_speed_powerup = speed_powerup_tuple[0]
    speed_powerup_object = speed_powerup_tuple[1][0]
    print(server_speed_boost_to_player_speed_boost)
    player_speed_power_up = server_speed_boost_to_player_speed_boost[server_speed_powerup]
    canvas.delete(player_speed_power_up)
    IncreaseSpeed()


def OtherConsumeSpeedPowerUp(other_player_speed_powerup_tuple):
    print(other_player_speed_powerup_tuple)
    other_player = other_player_speed_powerup_tuple[0]
    server_speed_powerup = other_player_speed_powerup_tuple[1][0]
    speed_powerup_object = other_player_speed_powerup_tuple[1][1][0]
    speed_powerup = server_speed_boost_to_player_speed_boost[server_speed_powerup]
    canvas.delete(speed_powerup)
    # for player in players_to_dots:
    #     if player.address == other_player.address:
    #         players_to_dots[other_player] = grow_dot(players_to_dots[player], other_player.color)
    #         break


def YouLose(data_object):
    messagebox.showinfo("Game Over", "You Lose")
    root.destroy()


def KillPlayer(other_player):
    global my_dot
    my_dot = grow_dot(my_dot, my_color)
    for player in players_to_dots:
        if player.address == other_player.address:
            dot_to_delete = players_to_dots.pop(player)
            canvas.delete(dot_to_delete)
            break
    else:
        raise Exception("Kill none existing player")


def PlayerDied(died_player: Player):
    for player in list(players_to_dots.keys()):
        if player.address == died_player.address:
            died_player_dot = players_to_dots.pop(player)
            canvas.delete(died_player_dot)


def PlayerOverSpeed(died_player: Player):
    for player in list(players_to_dots.keys()):
        if player.address == died_player.address:
            died_player_dot = players_to_dots.pop(player)
            canvas.delete(died_player_dot)
            # explosion_frames = [tk.PhotoImage(file=f"Animation\\Explosion\\explosion{i}.png") for i in range(1, 49)]
            lighting_frames = [tk.PhotoImage(file=f"Animation\\Lighting\\lightning{i}.png") for i in range(1, 93)]

            lighting_iter = iter(lighting_frames)
            animate_lighting(died_player.position_x, died_player.position_y, lighting_iter)


def YouOverSpeed(player: Player):
    # explosion_frames = [tk.PhotoImage(file=f"Animation\\Explosion\\explosion{i}.png") for i in range(1, 49)]
    canvas.unbind_all('<KeyPress>')
    lighting_frames = [tk.PhotoImage(file=f"Animation\\Lighting\\lightning{i}.png") for i in range(1, 93)]

    lighting_iter = iter(lighting_frames)
    animate_lighting(player.position_x, player.position_y, lighting_iter)
    messagebox.showinfo("Game Over", "You got electrocuted")
    root.destroy()


def PlayerTouchFlame(died_player: Player):
    for player in list(players_to_dots.keys()):
        if player.address == died_player.address:
            died_player_dot = players_to_dots.pop(player)
            canvas.delete(died_player_dot)
            explosion_frames = [tk.PhotoImage(file=f"Animation\\Explosion\\explosion{i}.png") for i in range(1, 49)]

            explosion_iter = iter(explosion_frames)
            animate_explosion(died_player.position_x, died_player.position_y, explosion_iter)

def YouTouchFlame(player: Player):
    canvas.unbind_all('<KeyPress>')
    explosion_frames = [tk.PhotoImage(file=f"Animation\\Explosion\\explosion{i}.png") for i in range(1, 49)]
    explosion_iter = iter(explosion_frames)
    animate_explosion(player.position_x, player.position_y, explosion_iter)
    messagebox.showinfo("Game Over", "You exploded")
    root.destroy()


def PlayerGrow(kill_player: Player):
    for player in list(players_to_dots.keys()):
        if player.address == kill_player.address:
            kill_player_dot = grow_dot(players_to_dots[player], kill_player.color)
            players_to_dots[player] = kill_player_dot


def listen_to_server(client_socket, a):
    while True:
        data, address = client_socket.recvfrom(1024)
        message = pickle.loads(data)
        print(f"Received from server: {message} from {address}")
        data_message = message[0]
        data_object = message[1]
        if data_message.startswith('You Consume PowerUps'):
            YouConsumePowerUp(data_object)
        elif data_message.startswith('Other Consume PowerUps'):
            OtherConsumePowerUp(data_object)
        elif data_message.startswith('You Consume SpeedPowerUps'):
            YouConsumeSpeedPowerUp(data_object)
        elif data_message.startswith('Other Consume SpeedPowerUps'):
            OtherConsumeSpeedPowerUp(data_object)
        elif data_message.startswith('PowerUps'):
            AssemblePowerUps(data_object)
        elif data_message.startswith('Fences'):
            AssembleFences(data_object)
        elif data_message.startswith('Flame'):
            AssembleFlame(data_object)
        elif data_message.startswith('Speed_boost'):
            AssembleSpeedBoost(data_object)
        elif data_message.startswith('Update: a new player connected'):
            CreateNewOtherPlayer(data_object)
        elif data_message.startswith('Get: other player'):
            GetOtherPlayer(data_object)
        elif data_message.startswith('UpdateMove: other player'):
            UpdateMoveOtherPlayer(data_object)
        elif data_message.startswith('Player Grow'):
            PlayerGrow(data_object)
        elif data_message.startswith('Player died'):
            PlayerDied(data_object)
        elif data_message.startswith('You OverSpeed'):
            YouOverSpeed(data_object)
        elif data_message.startswith('Player OverSpeed'):
            PlayerOverSpeed(data_object)
        elif data_message.startswith('You TouchFlame'):
            YouTouchFlame(data_object)
        elif data_message.startswith('Player TouchFlame'):
            PlayerTouchFlame(data_object)
        elif data_message.startswith('Kill Player'):
            KillPlayer(data_object)
        elif data_message.startswith('You Lose'):
            YouLose(data_object)


def Login():
    login_root = tk.Tk()
    global my_dot
    global my_color
    global my_name
    login_root.withdraw()  # Hide the main window

    login_window = LoginWindow(login_root)
    login_root.mainloop()
    my_color = login_window.get_color()
    my_name = login_window.get_name()

    if my_name is not None and my_color is not None:
        return my_name, my_color
    else:
        raise Exception('exit game')



def animate_flame():
    global flame_cycle
    img = next(flame_cycle)
    canvas.delete('flame')  # remove the previous flame image
    canvas.create_image(flame_pos_x, flame_pos_y, image=img, tags='flame')
    time.sleep(1)
    root.after(1000, animate_flame())  # continue the animation

def AssembleFlame(flame_tuple):
    global flame_pos_x
    global flame_pos_y
    global flame_cycle
    flame_pos_x = flame_tuple[0]
    flame_pos_y = flame_tuple[1]
    flame_images = [tk.PhotoImage(file=f"Animation\\Flames\\{i}.png") for i in range(1,5)]
    flame_cycle = cycle(flame_images)
    threading.Thread(target=animate_flame, daemon=True).start()

def main():
    global my_dot
    global my_color
    global my_name
    global root
    global canvas
    global flame_cycle
    my_name, my_color = Login()
    root = tk.Tk()
    canvas = tk.Canvas(root, width=board_width, height=board_height)
    canvas.pack()
    # Load your flame images
    # flame_images = [tk.PhotoImage(file=f"Animation\\Explosion\\explosion{i}.png") for i in range(10, 31, 10)]
    # flame_cycle = cycle(flame_images)
    # threading.Thread(target=animate_flame, daemon=True).start()

    # animate_flame()
    # Position for the flaming area
    x, y = 400, 300  # example position

    x = int((random.randint(0, int(800 / 10))) * 10)
    y = int((random.randint(0, int(600 / 10))) * 10)
    my_dot = canvas.create_oval(50, 50, 60, 60, fill=my_color)
    canvas.moveto(my_dot, x, y)
    print(canvas.coords(my_dot))
    canvas.bind_all('<KeyPress>', lambda event: move_dot(client_socket, event, my_dot, server_address))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 12345)  # Adjust to your server's address and port
    message = f"{my_name},{x},{y},0,{my_color}"
    client_socket.sendto(message.encode('utf-8'), server_address)

    threading.Thread(target=listen_to_server, args=(client_socket, canvas), daemon=True).start()

    # Create a dot

    root.mainloop()

    print('socket close')


if __name__ == "__main__":
    main()
