import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox


class LoginWindow(tk.Toplevel):
    def __init__(self, login_root):
        super().__init__(login_root)
        self.login_root = login_root
        self.player_name = None
        self.player_color = None

        self.title("Login")
        self.geometry("300x300")  # Set window size to 300x300

        # Center the grid columns and rows
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for i in range(20):
            self.grid_rowconfigure(i, weight=1)

        # Create label and entry for player name
        self.name_label = tk.Label(self, text="Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Button to choose color
        self.choose_color_btn = tk.Button(self, text="Choose Color", command=self.choose_color)
        self.choose_color_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Login button
        self.login_btn = tk.Button(self, text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event

        # time.sleep(3)
        #
        # while True:
        #     if self.name_label is not None and self.player_color is not None:
        #         break

    def get_name(self):
        return self.player_name

    def get_color(self):
        return self.player_color

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose dot color")[1]
        if color:
            self.player_color = color

    def on_closing(self):
        # This method gets triggered when the window is closed
        messagebox.showinfo("Login closed", "Exit")

        print(self.name_label, self.player_color)
        # self.destroy()  # Destroy the LoginWindow
        self.login_root.destroy()  # Destroy the root window

    def login(self):
        self.player_name = self.name_entry.get()
        print(self.player_name)

        if not self.player_name and not self.player_color:
            messagebox.showerror("Error", "Please input name and choose a color")
            return
        if not self.player_name:
            messagebox.showerror("Error", "Please choose Name")
            return
        if not self.player_color:
            messagebox.showerror("Error", "Please choose Color")
            return
        print(f"finished login window: name = {self.player_name}, color= {self.player_color}")
        # self.destroy()  # Destroy the LoginWindow
        self.login_root.destroy()  # Destroy the root window

