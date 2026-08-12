import os
import json
import tkinter as tk
from pynput import keyboard

CONFIG_FILE = "pokecount_config.json"

THEMES = {
    "kyogre": {
        "bg": "#0b1329", "card": "#131f38", "active": "#1b2c4f",
        "border": "#1e345c", "accent": "#38bdf8", "text": "#ffffff", "sub": "#94a3b8"
    },
    "Groudon": {
        "bg": "#0f0505", "card": "#1f0a0a", "active": "#330d0d",
        "border": "#4a1212", "accent": "#f43f5e", "text": "#fff1f2", "sub": "#fda4af"
    },
    "Rayquaza": {
        "bg": "#061a14", "card": "#0d2b22", "active": "#133f32",
        "border": "#1b4d3e", "accent": "#34d399", "text": "#ecfdf5", "sub": "#6ee7b7"
    },       
    "Ho-Oh": {
        "bg": "#1c1917", "card": "#292524", "active": "#44403c",
        "border": "#78716c", "accent": "#eab308", "text": "#fafaf9", "sub": "#d6d3d1"
    },
    "Gengar": {
        "bg": "#121212", "card": "#1e1e1e", "active": "#2c2c2c",
        "border": "#333333", "accent": "#a855f7", "text": "#f3f4f6", "sub": "#9ca3af"
    }
}

class PokeCountApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.90, "-topmost", True)
        
        # Load config or set defaults
        data = self.load_config()
        self.t_name = data.get("theme", "Gengar")
        if self.t_name not in THEMES: self.t_name = "Gengar"
        self.t = THEMES[self.t_name]
        self.scale = data.get("scale", 1.0)
        self.hotkeys = data.get("hotkeys", {"inc": "f1", "dec": "f2", "pause": "f3", "cycle": "f4"})
        
        raw_counters = data.get("counters", [
            {"name": "Counter 1", "count": 0},
            {"name": "Counter 2", "count": 0},
            {"name": "Counter 3", "count": 0}
        ])
        self.counters = [{"name": c["name"], "count": tk.IntVar(value=c["count"])} for c in raw_counters]
        
        self.root.configure(bg=self.t["bg"])
        self.paused = False
        self.active_idx = 0
        if self.active_idx >= len(self.counters): self.active_idx = 0
        
        # Build UI Container
        self.main = tk.Frame(self.root, bg=self.t["bg"])
        self.main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        self.status = tk.Label(self.main, bg=self.t["bg"], fg=self.t["sub"])
        self.status.pack(anchor="w", pady=(0, 3))
        
        self.cards = tk.Frame(self.main, bg=self.t["bg"])
        self.cards.pack(fill=tk.BOTH, expand=True)
        
        self.update_styles()
        self.refresh()
        
        # Smooth Draggable Window Handling
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", self.context_menu)
        
        # Keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self._x
        y = self.root.winfo_pointery() - self._y
        self.root.geometry(f"+{x}+{y}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        data = {
            "theme": self.t_name,
            "scale": self.scale,
            "hotkeys": self.hotkeys,
            "counters": [{"name": c["name"], "count": c["count"].get()} for c in self.counters]
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    def update_styles(self):
        self.f_status = max(6, int(7 * self.scale))
        self.f_name = max(7, int(9 * self.scale))
        self.f_btn = max(6, int(8 * self.scale))
        self.f_count = max(8, int(10 * self.scale))
        
        self.status.config(font=("Segoe UI", self.f_status))
        s = "⏸ PAUSED" if self.paused else f"≡ Poke-Count [{self.hotkeys['pause'].upper()}:Pause | {self.hotkeys['cycle'].upper()}:Switch]"
        self.status.config(text=s, fg="#f87171" if self.paused else self.t["sub"])

    def refresh(self):
        for w in self.cards.winfo_children(): w.destroy()
        for i, c in enumerate(self.counters):
            active = (i == self.active_idx)
            bg = self.t["active"] if active else self.t["card"]
            
            card = tk.Frame(self.cards, bg=bg, highlightbackground=self.t["accent"] if active else self.t["border"], highlightthickness=1)
            card.pack(fill=tk.X, pady=2)
            
            tk.Label(card, text=c['name'], font=("Segoe UI", self.f_name, "bold" if active else "normal"), fg=self.t["accent"] if active else self.t["sub"], bg=bg, width=12, anchor="w").pack(side=tk.LEFT, padx=6, pady=3)
            tk.Button(card, text="+", font=("Segoe UI", self.f_btn, "bold"), bg=self.t["card"], fg=self.t["accent"], relief=tk.FLAT, width=2, command=lambda idx=i: self.mod(idx, 1)).pack(side=tk.RIGHT, padx=2, pady=2)
            tk.Button(card, text="-", font=("Segoe UI", self.f_btn, "bold"), bg=self.t["card"], fg=self.t["accent"], relief=tk.FLAT, width=2, command=lambda idx=i: self.mod(idx, -1)).pack(side=tk.RIGHT, padx=2, pady=2)
            tk.Label(card, textvariable=c['count'], font=("Segoe UI", self.f_count, "bold"), fg=self.t["text"], bg=bg, width=3, anchor="e").pack(side=tk.RIGHT, padx=6)

    def mod(self, i, amt):
        if not self.paused and self.counters[i]['count'].get() + amt >= 0:
            self.counters[i]['count'].set(self.counters[i]['count'].get() + amt)
            self.save_config()

    def set_amount_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Set Amount")
        win.geometry("220x130")
        win.configure(bg=self.t["bg"])
        win.attributes("-topmost", True)
        win.grab_set()
        
        active_c = self.counters[self.active_idx]
        
        tk.Label(win, text=f"Set value for: {active_c['name']}", font=("Segoe UI", 8, "bold"), fg=self.t["text"], bg=self.t["bg"]).pack(pady=(10, 4))
        
        ent = tk.Entry(win, font=("Segoe UI", 10), bg=self.t["card"], fg=self.t["text"], insertbackground=self.t["text"], relief=tk.FLAT, justify="center", width=12)
        ent.insert(0, str(active_c['count'].get()))
        ent.pack(pady=4)
        ent.select_range(0, tk.END)
        ent.focus_set()

        def apply_val(event=None):
            try:
                val = int(ent.get().strip())
                if val >= 0:
                    active_c['count'].set(val)
                    self.save_config()
            except ValueError:
                pass
            win.destroy()

        tk.Button(win, text="Confirm", font=("Segoe UI", 8, "bold"), bg=self.t["accent"], fg=self.t["bg"], activebackground=self.t["sub"], activeforeground=self.t["bg"], relief=tk.FLAT, padx=10, pady=3, command=apply_val).pack(pady=6)
        ent.bind("<Return>", apply_val)

    def context_menu(self, event):
        m = tk.Menu(self.root, tearoff=0, bg=self.t["card"], fg=self.t["text"], relief=tk.FLAT)
        m.add_command(label="⚙ Settings", command=self.settings)
        m.add_command(label="✏ Set Amount...", command=self.set_amount_dialog)
        m.add_command(label="↺ Reset Active", command=lambda: [self.counters[self.active_idx]['count'].set(0), self.save_config()])
        m.add_command(label="↺ Reset All", command=lambda: [c['count'].set(0) for c in self.counters] or self.save_config())
        m.add_separator()
        m.add_command(label="✕ Close", command=self.cleanup)
        try: m.tk_popup(event.x_root, event.y_root)
        finally: m.grab_release()

    def settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("280x560")
        win.configure(bg=self.t["bg"])
        win.attributes("-topmost", True)
        win.grab_set()
        
        tk.Label(win, text="Manage Rows & Binds", font=("Segoe UI", 9, "bold"), fg=self.t["text"], bg=self.t["bg"]).pack(pady=(10, 4))
        
        rf = tk.Frame(win, bg=self.t["bg"])
        rf.pack(fill=tk.BOTH, expand=True, padx=12)
        
        ents = []
        def delete_row_action(idx):
            self.counters.pop(idx)
            if self.active_idx >= len(self.counters):
                self.active_idx = max(0, len(self.counters) - 1)
            rebuild_r()

        def rebuild_r():
            for w in rf.winfo_children(): w.destroy()
            ents.clear()
            for i, c in enumerate(self.counters):
                row = tk.Frame(rf, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
                row.pack(fill=tk.X, pady=3, padx=2)
                
                ent = tk.Entry(row, font=("Segoe UI", 8), bg=self.t["bg"], fg=self.t["text"], insertbackground=self.t["text"], relief=tk.FLAT, width=14)
                ent.insert(0, c['name'])
                ent.pack(side=tk.LEFT, padx=6, pady=5)
                
                if len(self.counters) > 1:
                    tk.Button(row, text="✕", font=("Segoe UI", 7, "bold"), bg="#2a1f1f", fg="#f87171", activebackground="#3d2a2a", activeforeground="#f87171", relief=tk.FLAT, command=lambda idx=i: delete_row_action(idx)).pack(side=tk.RIGHT, padx=6)
                ents.append(ent)
        rebuild_r()
        
        def add_row_action():
            if len(self.counters) < 5:
                self.counters.append({"name": f"Counter {len(self.counters)+1}", "count": tk.IntVar(value=0)})
                rebuild_r()

        if len(self.counters) < 5:
            tk.Button(win, text="+ Add Row", font=("Segoe UI", 8, "bold"), bg=self.t["card"], fg=self.t["accent"], activebackground=self.t["active"], activeforeground=self.t["accent"], relief=tk.FLAT, padx=8, pady=3, command=add_row_action).pack(pady=4)

        # Scale Slider Panel
        sf = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        sf.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(sf, text="Scale / Size:", font=("Segoe UI", 7, "bold"), fg=self.t["sub"], bg=self.t["card"]).pack(anchor="w", padx=8, pady=(4,0))
        scale_slider = tk.Scale(sf, from_=0.7, to=1.6, resolution=0.1, orient=tk.HORIZONTAL, bg=self.t["card"], fg=self.t["text"], highlightthickness=0, troughcolor=self.t["bg"], activebackground=self.t["accent"])
        scale_slider.set(self.scale)
        scale_slider.pack(fill=tk.X, padx=8, pady=(0, 6))

        # Theme Selector Panel
        tf = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        tf.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(tf, text="Theme:", font=("Segoe UI", 7, "bold"), fg=self.t["sub"], bg=self.t["card"]).pack(anchor="w", padx=8, pady=(4,0))
        tv = tk.StringVar(value=self.t_name)
        
        theme_menu = tk.OptionMenu(tf, tv, *THEMES.keys())
        theme_menu.config(bg=self.t["bg"], fg=self.t["text"], activebackground=self.t["active"], activeforeground=self.t["text"], highlightthickness=0, bd=0, relief=tk.FLAT)
        theme_menu["menu"].config(bg=self.t["card"], fg=self.t["text"], activebackground=self.t["accent"], activeforeground=self.t["bg"])
        theme_menu.pack(fill=tk.X, padx=8, pady=(0, 6))

        # Hotkeys Panel
        hf = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        hf.pack(fill=tk.X, padx=12, pady=4)
        h_ents = {}
        for k, label in [("inc", "Increase:"), ("dec", "Decrease:"), ("pause", "Pause:"), ("cycle", "Switch:")]:
            r = tk.Frame(hf, bg=self.t["card"])
            r.pack(fill=tk.X, padx=8, pady=3)
            tk.Label(r, text=label, font=("Segoe UI", 7), fg=self.t["sub"], bg=self.t["card"], width=8, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(r, font=("Segoe UI", 8), bg=self.t["bg"], fg=self.t["text"], insertbackground=self.t["text"], relief=tk.FLAT, width=8)
            e.insert(0, self.hotkeys[k])
            e.pack(side=tk.RIGHT)
            h_ents[k] = e

        def save():
            for i, e in enumerate(ents): self.counters[i]['name'] = e.get().strip() or f"Counter {i+1}"
            for k in self.hotkeys: self.hotkeys[k] = h_ents[k].get().strip().lower()
            self.scale = scale_slider.get()
            self.t_name = tv.get()
            self.t = THEMES[self.t_name]
            
            if self.active_idx >= len(self.counters):
                self.active_idx = max(0, len(self.counters) - 1)
            
            self.root.configure(bg=self.t["bg"])
            self.main.configure(bg=self.t["bg"])
            self.cards.configure(bg=self.t["bg"])
            self.status.configure(bg=self.t["bg"])
            
            self.update_styles()
            self.refresh()
            self.save_config()
            win.destroy()

        tk.Button(win, text="Save Changes", font=("Segoe UI", 8, "bold"), bg=self.t["accent"], fg=self.t["bg"], activebackground=self.t["sub"], activeforeground=self.t["bg"], relief=tk.FLAT, padx=12, pady=5, command=save).pack(pady=10)

    def on_press(self, key):
        try:
            kid = key.name.lower() if hasattr(key, 'name') and key.name else (key.char.lower() if hasattr(key, 'char') and key.char else None)
            if not kid: return
            if kid == self.hotkeys["pause"]:
                self.paused = not self.paused
                self.root.after(0, self.update_styles)
            elif not self.paused:
                if kid == self.hotkeys["cycle"]:
                    self.active_idx = (self.active_idx + 1) % len(self.counters)
                    self.root.after(0, self.refresh)
                elif kid == self.hotkeys["inc"]:
                    self.root.after(0, lambda: self.mod(self.active_idx, 1))
                elif kid == self.hotkeys["dec"]:
                    self.root.after(0, lambda: self.mod(self.active_idx, -1))
        except: pass

    def cleanup(self):
        self.save_config()
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokeCountApp(root)
    root.mainloop()