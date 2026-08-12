# 🎮 Poke-Count
A standalone script built with Python and Tkinter, compiled into a exe to make manually tracking easier in pokeMMO ( perfect for box farming & breeders! )

## 🚀 Getting Started
[Click here](https://github.com/itzzzH/Poke-Count/releases/tag/1.0) to download the latest release ( .exe )

    Place it anywhere on your computer (it will create its own config file locally)

    Double-click to launch!

    Alternatively, you can run the source code yourself "pokecount.py" (requires pynput installed).
    
## Features

    Transparent & Always-on-Top: Built as a sleek borderless overlay that stays pinned over your game window (90% opacity).

    Multiple Counter Rows: Keep track of up to 5 different counters simultaneously with custom names (e.g., Ditto, Pikachu).

    Global Hotkeys: Control your counts seamlessly without tabbing out of the game:

    F1: Increase amount

    F2: Decrease amount

    F3: Pause / Unpause tracking

    F4: Switch between active rows

    Custom Themes: Includes several built-in colour schemes.

    Auto-Saving: Automatically remembers your counts, custom names, hotkeys, and theme preferences via a local JSON file (counter_config.json) when closed.

    Fully Scalable: Adjust the text size and scale slider through the settings panel to fit your preferred layout.

    Zero Bloat: Consumes minimal RAM (~15-25MB) and sits at 0% CPU usage when idle.

<img width="271" height="118" alt="image" src="https://github.com/user-attachments/assets/ba5a4370-17f2-4853-818f-eb2ca02ee244" />
<img width="296" height="497" alt="image" src="https://github.com/user-attachments/assets/34ddd6af-a9d3-402a-b8f7-06c928f6fa1a" />


## ⚙️ Settings & Customisation
Right-click the overlay and select Settings to:

    Add or delete tracking rows (up to 5).

    Rename your counter targets.

    Customise global hotkey bindings.

    Change UI themes and scaling size.

## Please note!
Because this is written in Python and compiled with PyInstaller and uses pynput to listen for global hotkeys while you're in-game some antivirus programs or VirusTotal scanners may show false positives. The full source code is completely open in this repo "pokecount.py" 

📦 What's inside the .exe?

Since this is packaged with PyInstaller so you don't have to mess around installing Python yourself, the .exe basically bundles a few things together:

    The actual PokeCount source code

    A lightweight, built-in Python runtime so it can execute

    The required packages—mainly pynput (for global hotkeys so you can count while tabbed into your game) and Tkinter (for the UI)

    A small bootloader that handles launching the app smoothly
