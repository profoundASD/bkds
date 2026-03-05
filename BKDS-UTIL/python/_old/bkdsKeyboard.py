import tkinter as tk
import subprocess

root = tk.Tk()

import subprocess

def show_keyboard():
    subprocess.Popen(["xdotool", "key", "super+space"])

# Create a button to show the keyboard
keyboard_button = tk.Button(root, text="Show keyboard", command=show_keyboard)
keyboard_button.pack()