import os
import json
import tkinter as tk
from pynput import keyboard

CONFIG_FILE = "pokecount_config.json"

THEMES = {
    "Groudon": {
        "bg": "#0a0505", "card": "#170a0a", "active": "#260f0f",
        "border": "#361616", "accent": "#ef4444", "text": "#fef2f2", "sub": "#fca5a5"
    },
    "kyogre": {
        "bg": "#0b1329", "card": "#131f38", "active": "#1b2c4f",
        "border": "#1e345c", "accent": "#38bdf8", "text": "#ffffff", "sub": "#94a3b8"
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
        "bg": "#000000", "card": "#121212", "active": "#1f1f1f",
        "border": "#2c2c2c", "accent": "#a855f7", "text": "#f3f4f6", "sub": "#9ca3af"
    },
    "Red": {
        "bg": "#000000", "card": "#121212", "active": "#1f1f1f",
        "border": "#2c2c2c", "accent": "#ef4444", "text": "#f3f4f6", "sub": "#9ca3af"
    },
    "White": {
        "bg": "#000000", "card": "#121212", "active": "#1f1f1f",
        "border": "#2c2c2c", "accent": "#ffffff", "text": "#ffffff", "sub": "#a1a1aa"
    }
}


class PokeCountApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.TRANSPARENT_COLOR = "#010101"
        self.root.config(bg=self.TRANSPARENT_COLOR)
        try:
            self.root.attributes("-transparentcolor", self.TRANSPARENT_COLOR)
        except Exception:
            pass
        
        data = self.load_config()
        self.t_name = data.get("theme", "Groudon")
        if self.t_name not in THEMES: self.t_name = "Groudon"
        self.t = THEMES[self.t_name]
        self.scale = data.get("scale", 1.0)
        self.opacity = data.get("opacity", 0.90)
        self.root.attributes("-alpha", self.opacity)
        
        self.hotkeys = data.get("hotkeys", {"inc": "f1", "dec": "f2", "pause": "f3", "cycle": "f4"})
        
        raw_counters = data.get("counters", [
            {"name": "Counter 1", "count": 0},
            {"name": "Counter 2", "count": 0},
            {"name": "Counter 3", "count": 0}
        ])
        self.counters = [{"name": c["name"], "count": tk.IntVar(value=c["count"])} for c in raw_counters]
        
        for c in self.counters:
            c["count"].trace_add("write", lambda *args: self.redraw_counts())

        self.paused = False
        self.active_idx = 0
        if self.active_idx >= len(self.counters): self.active_idx = 0
        
        self.main = tk.Frame(self.root, bg=self.TRANSPARENT_COLOR)
        self.main.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self.cards = tk.Frame(self.main, bg=self.TRANSPARENT_COLOR)
        self.cards.pack(fill=tk.BOTH, expand=True)
        
        self.row_widgets = []
        self.update_styles()
        self.build_ui()
        
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", self.context_menu)
        
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
            "opacity": self.opacity,
            "hotkeys": self.hotkeys,
            "counters": [{"name": c["name"], "count": c["count"].get()} for c in self.counters]
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    def update_styles(self):
        self.f_name = max(8, int(10 * self.scale))
        self.f_btn = max(7, int(9 * self.scale))
        self.f_count = max(9, int(11 * self.scale))

    def create_rounded_pill(self, parent, w, h, bg_color, border_color):
        cv = tk.Canvas(parent, width=w, height=h, bg=self.TRANSPARENT_COLOR, highlightthickness=0, bd=0)
        
        x1, y1, x2, y2 = 2, 2, w - 2, h - 2
        radius = int((h - 4) / 2)
        
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius,
            x2, y2, x2 - radius, y2,
            x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        
        cv.create_polygon(points, smooth=True, splinesteps=36, fill=bg_color, outline=border_color, width=1.5, tag="poly")
        return cv

    def build_ui(self):
        for w in self.cards.winfo_children(): w.destroy()
        self.row_widgets.clear()
        
        pill_w = int(220 * self.scale)
        pill_h = int(36 * self.scale)
        
        for i, c in enumerate(self.counters):
            active = (i == self.active_idx)
            bg = self.t["active"] if active else self.t["card"]
            border = self.t["accent"] if active else self.t["border"]
            
            wrapper = tk.Frame(self.cards, bg=self.TRANSPARENT_COLOR, width=pill_w, height=pill_h)
            wrapper.pack(fill=tk.X, pady=2)
            wrapper.pack_propagate(False)
            
            cv = self.create_rounded_pill(wrapper, pill_w, pill_h, bg, border)
            cv.pack(fill=tk.BOTH, expand=True)
            
            lbl_name = tk.Label(cv, text=c['name'], font=("Segoe UI", self.f_name, "bold"), fg=self.t["accent"] if active else self.t["sub"], bg=bg, anchor="w", width=9)
            cv.create_window(int(14 * self.scale), int(18 * self.scale), window=lbl_name, anchor="w")
            
            btn_plus = tk.Button(cv, text="+", font=("Consolas", self.f_btn, "bold"), bg=self.t["card"], fg=self.t["accent"], activebackground=self.t["border"], activeforeground=self.t["text"], relief=tk.FLAT, bd=0, highlightthickness=0, width=2, command=lambda idx=i: self.mod(idx, 1))
            cv.create_window(pill_w - int(12 * self.scale), int(18 * self.scale), window=btn_plus, anchor="e")
            
            btn_minus = tk.Button(cv, text="-", font=("Consolas", self.f_btn, "bold"), bg=self.t["card"], fg=self.t["accent"], activebackground=self.t["border"], activeforeground=self.t["text"], relief=tk.FLAT, bd=0, highlightthickness=0, width=2, command=lambda idx=i: self.mod(idx, -1))
            cv.create_window(pill_w - int(38 * self.scale), int(18 * self.scale), window=btn_minus, anchor="e")
            
            count_text_id = cv.create_text(
                pill_w - int(72 * self.scale), int(18 * self.scale),
                text=str(c['count'].get()),
                font=("Consolas", self.f_count, "bold"),
                fill=self.t["text"],
                anchor="center",
                tags="count_txt"
            )
            
            self.row_widgets.append({
                "canvas": cv, "name_label": lbl_name, "count_text_id": count_text_id
            })

    def redraw_counts(self):
        for i, item in enumerate(self.counters):
            if i < len(self.row_widgets):
                w_info = self.row_widgets[i]
                w_info["canvas"].itemconfig(w_info["count_text_id"], text=str(item['count'].get()))

    def update_active_states(self):
        for i, item in enumerate(self.row_widgets):
            active = (i == self.active_idx)
            bg = self.t["active"] if active else self.t["card"]
            border = self.t["accent"] if active else self.t["border"]
            
            cv = item["canvas"]
            cv.itemconfig("poly", fill=bg, outline=border)
            
            item["name_label"].config(
                fg=self.t["accent"] if active else self.t["sub"],
                bg=bg
            )

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
        tk.Label(win, text=f"Set value for: {active_c['name']}", font=("Segoe UI", 9, "bold"), fg=self.t["text"], bg=self.t["bg"]).pack(pady=(10, 4))
        
        ent = tk.Entry(win, font=("Consolas", 11, "bold"), bg=self.t["card"], fg=self.t["text"], insertbackground=self.t["text"], relief=tk.FLAT, justify="center", width=12)
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
        win.geometry("280x620")
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

        sf = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        sf.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(sf, text="Scale / Size:", font=("Segoe UI", 7, "bold"), fg=self.t["sub"], bg=self.t["card"]).pack(anchor="w", padx=8, pady=(4,0))
        scale_slider = tk.Scale(sf, from_=0.7, to=1.6, resolution=0.1, orient=tk.HORIZONTAL, bg=self.t["card"], fg=self.t["text"], highlightthickness=0, troughcolor=self.t["bg"], activebackground=self.t["accent"])
        scale_slider.set(self.scale)
        scale_slider.pack(fill=tk.X, padx=8, pady=(0, 6))

        op_f = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        op_f.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(op_f, text="Opacity:", font=("Segoe UI", 7, "bold"), fg=self.t["sub"], bg=self.t["card"]).pack(anchor="w", padx=8, pady=(4,0))
        
        def update_opacity(val):
            self.root.attributes("-alpha", float(val))

        opacity_slider = tk.Scale(op_f, from_=0.2, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, bg=self.t["card"], fg=self.t["text"], highlightthickness=0, troughcolor=self.t["bg"], activebackground=self.t["accent"], command=update_opacity)
        opacity_slider.set(self.opacity)
        opacity_slider.pack(fill=tk.X, padx=8, pady=(0, 6))

        tf = tk.Frame(win, bg=self.t["card"], highlightbackground=self.t["border"], highlightthickness=1)
        tf.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(tf, text="Theme:", font=("Segoe UI", 7, "bold"), fg=self.t["sub"], bg=self.t["card"]).pack(anchor="w", padx=8, pady=(4,0))
        tv = tk.StringVar(value=self.t_name)
        
        theme_menu = tk.OptionMenu(tf, tv, *THEMES.keys())
        theme_menu.config(bg=self.t["bg"], fg=self.t["text"], activebackground=self.t["active"], activeforeground=self.t["text"], highlightthickness=0, bd=0, relief=tk.FLAT)
        theme_menu["menu"].config(bg=self.t["card"], fg=self.t["text"], activebackground=self.t["accent"], activeforeground=self.t["bg"])
        theme_menu.pack(fill=tk.X, padx=8, pady=(0, 6))

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
            self.opacity = opacity_slider.get()
            self.t_name = tv.get()
            self.t = THEMES[self.t_name]
            
            if self.active_idx >= len(self.counters):
                self.active_idx = max(0, len(self.counters) - 1)
            
            self.root.attributes("-alpha", self.opacity)
            self.update_styles()
            self.build_ui()
            self.save_config()
            win.destroy()

        tk.Button(win, text="Save Changes", font=("Segoe UI", 8, "bold"), bg=self.t["accent"], fg=self.t["bg"], activebackground=self.t["sub"], activeforeground=self.t["bg"], relief=tk.FLAT, padx=12, pady=5, command=save).pack(pady=10)

    def on_press(self, key):
        try:
            kid = key.name.lower() if hasattr(key, 'name') and key.name else (key.char.lower() if hasattr(key, 'char') and key.char else None)
            if not kid: return
            if kid == self.hotkeys["pause"]:
                self.paused = not self.paused
            elif not self.paused:
                if kid == self.hotkeys["cycle"]:
                    self.active_idx = (self.active_idx + 1) % len(self.counters)
                    self.root.after(0, self.update_active_states)
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