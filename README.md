🎮 PokeMMO Encounter Tracker Overlay

A lightweight, transparent, and customizable micro-overlay designed specifically for tracking encounters (and shiny hunting!) in PokeMMO.

Built with Python and Tkinter, it sits cleanly on top of your game without getting in the way, running quietly with a tiny footprint.
✨ Features

    Transparent & Always-on-Top: Built as a sleek borderless overlay that stays pinned over your game window (90% opacity).

    Multiple Counter Rows: Track up to 5 different encounters/Pokémon simultaneously with custom names (e.g., Ditto, Pikachu).

    Global Hotkeys: Control your counts seamlessly without tabbing out of the game:

        F1: Increment active counter

        F2: Decrement active counter

        F3: Pause / Unpause tracking

        F4: Switch between active counter rows

    Custom Themes: Includes several built-in color schemes, featuring classic Pokémon-inspired aesthetics (Midnight Blue, Kanto Pokéball, Johto Gold/Silver, Team Rocket, and more).

    Auto-Saving: Automatically remembers your counts, custom names, hotkeys, and theme preferences via a local JSON file (counter_config.json) when closed.

    Fully Scalable: Adjust the text size and scale slider through the settings panel to fit your preferred layout.

    Zero Bloat: Consumes minimal RAM (~15-25MB) and sits at 0% CPU usage when idle.

🚀 Getting Started (For Users)

If you just downloaded the compiled version from the releases page:

    Download the latest counter.exe.

    Place it anywhere on your computer (it will create its own config file locally).

    Double-click to launch!

Controls & Right-Click Menu

    Drag Window: Click and drag anywhere on the overlay to move it around your screen.

    Right-Click: Open the context menu to access Settings & Rows, Reset Active, Reset All, or Close the app.

⚙️ Settings & Customization

Right-click the overlay and select Settings & Rows to:

    Add or delete tracking rows (up to 5).

    Rename your encounter targets.

    Customize global hotkey bindings.

    Change UI themes and scaling size.

🛠️ Running from Source & Building (For Developers)

If you want to run the raw Python script or build your own .exe file using PyInstaller:
Prerequisites

    Python 3.x installed on your system.

    Install the required global hotkey library (pynput):
