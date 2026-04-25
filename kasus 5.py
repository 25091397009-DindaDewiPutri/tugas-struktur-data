"""
Queue Visualizations - Python Tkinter Version
5 Implementasi Queue dalam Kasus Nyata
Jalankan: python queue_visualizations.py
"""

import tkinter as tk
from tkinter import ttk, font
import math
import random
import time
from collections import deque

# ─────────────────────────── WARNA TEMA ───────────────────────────
BG_DARK    = "#0a0e27"
BG_CARD    = "#141932"
CYAN       = "#00d9ff"
PURPLE     = "#b537f2"
PINK       = "#ff2e97"
YELLOW     = "#ffbe0b"
WHITE      = "#ffffff"
GRAY       = "#a0a8c4"
GREEN      = "#2ecc71"
RED        = "#ff2e97"
BORDER     = "#1e2a50"


# ══════════════════════════════════════════════════════════════════
#   HELPER WIDGET
# ══════════════════════════════════════════════════════════════════

def make_btn(parent, text, command, color=PURPLE):
    """Tombol bergaya neon."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=WHITE, activebackground=CYAN, activeforeground=BG_DARK,
        font=("Courier New", 9, "bold"), relief="flat", bd=0,
        padx=12, pady=6, cursor="hand2"
    )
    return btn

def make_label(parent, text, fg=CYAN, font_size=9, bold=False):
    style = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=BG_CARD, fg=fg,
                    font=("Courier New", font_size, style))

def make_status(parent, text):
    frame = tk.Frame(parent, bg="#0d1530", bd=0)
    lbl = tk.Label(frame, text=text, bg="#0d1530", fg=GRAY,
                   font=("Courier New", 9), wraplength=900, justify="left",
                   padx=10, pady=8)
    lbl.pack(fill="x")
    # garis kiri cyan
    frame.config(highlightbackground=CYAN, highlightthickness=0)
    left_bar = tk.Frame(frame, bg=CYAN, width=4)
    left_bar.place(x=0, y=0, relheight=1)
    return frame, lbl

def card_frame(parent, title, number):
    """Membuat kartu dengan judul."""
    outer = tk.Frame(parent, bg=BG_CARD, bd=2, relief="flat",
                     highlightbackground=BORDER, highlightthickness=2)

    # Header
    header = tk.Frame(outer, bg=BG_CARD)
    header.pack(fill="x", padx=15, pady=(15, 5))

    num_lbl = tk.Label(header, text=str(number), bg=PURPLE, fg=WHITE,
                       font=("Courier New", 14, "bold"), width=3, height=1,
                       relief="flat")
    num_lbl.pack(side="left", padx=(0, 10))

    tk.Label(header, text=title, bg=BG_CARD, fg=CYAN,
             font=("Courier New", 12, "bold")).pack(side="left")

    return outer


# ══════════════════════════════════════════════════════════════════
#   KASUS 1: PRINTER QUEUE
# ══════════════════════════════════════════════════════════════════

class PrinterCase:
    DOCS = ['laporan.pdf', 'tugas.docx', 'foto.jpg',
            'presentasi.pptx', 'data.xlsx', 'memo.pdf']

    def __init__(self, parent):
        self.queue = deque()
        self.doc_idx = 0

        card = card_frame(parent, "Antrian Printer Bersama", 1)
        card.pack(fill="x", padx=20, pady=10)

        # Tombol
        btns = tk.Frame(card, bg=BG_CARD)
        btns.pack(fill="x", padx=15, pady=5)
        make_btn(btns, "Tambah Dokumen", self.add_job).pack(side="left", padx=3)
        make_btn(btns, "Cetak Dokumen",  self.process_print).pack(side="left", padx=3)
        make_btn(btns, "Reset", self.reset, color="#333a5c").pack(side="left", padx=3)

        # Visualisasi
        viz = tk.Frame(card, bg="#0a0e27", bd=0, pady=15)
        viz.pack(fill="x", padx=15, pady=5)
        self.canvas = tk.Canvas(viz, bg="#0a0e27", height=80,
                                highlightthickness=0)
        self.canvas.pack(fill="x", padx=10)

        # Status
        sf, self.status_lbl = make_status(card,
            'Printer siap. Klik "Tambah Dokumen" untuk menambah ke antrian.')
        sf.pack(fill="x", padx=15, pady=(0, 12))

        self.draw_queue()

    def draw_queue(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 900
        if not self.queue:
            c.create_text(w // 2, 40, text="[ Kosong ]",
                          fill=GRAY, font=("Courier New", 11))
            return

        items = list(self.queue)
        box_w, box_h, gap = 120, 44, 12
        total = len(items) * box_w + (len(items) - 1) * gap
        x0 = max(10, (w - total) // 2)

        # Label DEPAN
        c.create_text(x0 - 8, 40, text="DEPAN→", fill=CYAN,
                      font=("Courier New", 8, "bold"), anchor="e")

        for i, doc in enumerate(items):
            x = x0 + i * (box_w + gap)
            # kotak gradasi (simulasi dengan dua rect)
            c.create_rectangle(x, 18, x + box_w, 18 + box_h,
                               fill=PURPLE, outline=CYAN, width=1)
            c.create_rectangle(x + 2, 20, x + box_w - 2, 18 + box_h - 2,
                               fill="#7b2fbe", outline="")
            c.create_text(x + box_w // 2, 18 + box_h // 2,
                          text=doc, fill=WHITE,
                          font=("Courier New", 8, "bold"))
            if i < len(items) - 1:
                ax = x + box_w + 2
                c.create_text(ax + gap // 2, 40, text="→",
                              fill=YELLOW, font=("Courier New", 14, "bold"))

        # Label BELAKANG
        ex = x0 + len(items) * (box_w + gap) - gap + 5
        c.create_text(ex, 40, text="←BELAKANG", fill=CYAN,
                      font=("Courier New", 8, "bold"), anchor="w")

    def add_job(self):
        doc = self.DOCS[self.doc_idx % len(self.DOCS)]
        self.doc_idx += 1
        self.queue.append(doc)
        self.status_lbl.config(text=f"✓ Ditambahkan: {doc}")
        self.draw_queue()

    def process_print(self):
        if not self.queue:
            self.status_lbl.config(text="⚠ Antrian kosong!")
            return
        doc = self.queue.popleft()
        self.status_lbl.config(text=f"🖨 Mencetak: {doc}")
        self.draw_queue()

    def reset(self):
        self.queue.clear()
        self.doc_idx = 0
        self.status_lbl.config(
            text='Printer siap. Klik "Tambah Dokumen" untuk menambah ke antrian.')
        self.draw_queue()


# ══════════════════════════════════════════════════════════════════
#   KASUS 2: HOT POTATO
# ══════════════════════════════════════════════════════════════════

class HotPotatoCase:
    NAMES = ['Ana', 'Budi', 'Citra', 'Dedi', 'Eka', 'Fani']

    def __init__(self, parent):
        self.players = []
        self.active = False
        self.after_id = None

        card = card_frame(parent, "Permainan Hot Potato", 2)
        card.pack(fill="x", padx=20, pady=10)

        btns = tk.Frame(card, bg=BG_CARD)
        btns.pack(fill="x", padx=15, pady=5)
        make_btn(btns, "Mulai Permainan", self.start).pack(side="left", padx=3)
        make_btn(btns, "Reset", self.reset, color="#333a5c").pack(side="left", padx=3)

        viz = tk.Frame(card, bg="#0a0e27")
        viz.pack(fill="x", padx=15, pady=5)
        self.canvas = tk.Canvas(viz, bg="#0a0e27", height=340,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10)

        sf, self.status_lbl = make_status(card,
            'Klik "Mulai Permainan". Setelah 7 kali oper, satu pemain tersingkir!')
        sf.pack(fill="x", padx=15, pady=(0, 12))

        self.init_players()

    def init_players(self):
        self.players = [{"name": n, "eliminated": False} for n in self.NAMES]
        self.draw_players(-1)

    def draw_players(self, active_idx=-1):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 600
        cx, cy, r = w // 2, 160, 120
        active_list = [i for i, p in enumerate(self.players) if not p["eliminated"]]
        n = len(active_list)

        for rank, gi in enumerate(active_list):
            p = self.players[gi]
            angle = (rank / n) * 2 * math.pi - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)

            is_active = (rank == active_idx % n if active_idx >= 0 else False)
            color = YELLOW if is_active else CYAN
            outline = PINK if is_active else PURPLE
            radius = 34 if is_active else 28

            c.create_oval(px - radius, py - radius, px + radius, py + radius,
                          fill=color, outline=outline, width=3)
            c.create_text(px, py, text=p["name"], fill=BG_DARK if is_active else WHITE,
                          font=("Courier New", 9, "bold"))

        for gi, p in enumerate(self.players):
            if p["eliminated"]:
                angle = (gi / len(self.players)) * 2 * math.pi - math.pi / 2
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                c.create_oval(px - 24, py - 24, px + 24, py + 24,
                              fill="#333", outline="#555", width=2)
                c.create_text(px, py, text=p["name"], fill="#666",
                              font=("Courier New", 8))

    def start(self):
        if self.active:
            return
        active = [i for i, p in enumerate(self.players) if not p["eliminated"]]
        if len(active) <= 1:
            winner = self.players[active[0]]["name"] if active else "?"
            self.status_lbl.config(text=f"🏆 Pemenang: {winner}!")
            return

        self.active = True
        self.status_lbl.config(text="🥔 Mengoper kentang...")
        self._pass_step(0, active)

    def _pass_step(self, step, active):
        if step < 7:
            idx = step % len(active)
            self.draw_players(idx)
            self.after_id = self.canvas.after(
                300, lambda: self._pass_step(step + 1, active))
        else:
            elim_rank = 7 % len(active)
            elim_gi = active[elim_rank]
            self.players[elim_gi]["eliminated"] = True
            name = self.players[elim_gi]["name"]
            remaining = sum(1 for p in self.players if not p["eliminated"])
            self.status_lbl.config(
                text=f"❌ {name} tersingkir! {remaining} pemain tersisa.")
            self.draw_players(-1)
            self.active = False

    def reset(self):
        if self.after_id:
            self.canvas.after_cancel(self.after_id)
        self.active = False
        self.init_players()
        self.status_lbl.config(
            text='Klik "Mulai Permainan". Setelah 7 kali oper, satu pemain tersingkir!')


# ══════════════════════════════════════════════════════════════════
#   KASUS 3: HOSPITAL PRIORITY QUEUE
# ══════════════════════════════════════════════════════════════════

class HospitalCase:
    PRIORITIES = ["critical", "emergency", "medium", "low"]
    LABELS = {
        "critical":  ("🔴 Kritis",   "#ff2e97"),
        "emergency": ("🟡 Darurat",  YELLOW),
        "medium":    ("🔵 Menengah", CYAN),
        "low":       ("⚪ Ringan",   GRAY),
    }
    BTN_COLORS = {
        "critical": "#c0135a", "emergency": "#c88a00",
        "medium": "#007aaa", "low": "#444"
    }

    def __init__(self, parent):
        self.queues = {p: deque() for p in self.PRIORITIES}
        self.counter = 1

        card = card_frame(parent, "Antrian Rumah Sakit (Priority Queue)", 3)
        card.pack(fill="x", padx=20, pady=10)

        btns = tk.Frame(card, bg=BG_CARD)
        btns.pack(fill="x", padx=15, pady=5)
        for p in self.PRIORITIES:
            label, _ = self.LABELS[p]
            make_btn(btns, label,
                     lambda pr=p: self.add_patient(pr),
                     color=self.BTN_COLORS[p]).pack(side="left", padx=2)
        make_btn(btns, "Layani Pasien", self.serve).pack(side="left", padx=6)
        make_btn(btns, "Reset", self.reset, color="#333a5c").pack(side="left", padx=2)

        viz = tk.Frame(card, bg="#0a0e27", pady=10)
        viz.pack(fill="x", padx=15, pady=5)

        self.row_frames = {}
        self.row_canvases = {}
        for p in self.PRIORITIES:
            label_text, col = self.LABELS[p]
            row = tk.Frame(viz, bg="#0a0e27")
            row.pack(fill="x", pady=4, padx=10)
            tk.Label(row, text=label_text, bg="#0a0e27", fg=col,
                     font=("Courier New", 9, "bold"), width=13,
                     anchor="w").pack(side="left")
            c = tk.Canvas(row, bg="#0a0e27", height=40, highlightthickness=0)
            c.pack(side="left", fill="x", expand=True)
            self.row_canvases[p] = c
            self.row_frames[p] = row

        sf, self.status_lbl = make_status(card,
            "Tambahkan pasien. Pasien prioritas tinggi dilayani lebih dulu.")
        sf.pack(fill="x", padx=15, pady=(0, 12))

        self.draw_all()

    def draw_row(self, priority):
        c = self.row_canvases[priority]
        c.delete("all")
        items = list(self.queues[priority])
        _, col = self.LABELS[priority]
        if not items:
            c.create_text(50, 20, text="Kosong", fill=GRAY,
                          font=("Courier New", 9))
            return
        bw = 52
        for i, name in enumerate(items):
            x = 5 + i * (bw + 6)
            c.create_rectangle(x, 5, x + bw, 35, fill=col,
                               outline=WHITE, width=1)
            c.create_text(x + bw // 2, 20, text=name, fill=BG_DARK,
                          font=("Courier New", 9, "bold"))

    def draw_all(self):
        for p in self.PRIORITIES:
            self.draw_row(p)

    def add_patient(self, priority):
        name = f"P{self.counter}"
        self.counter += 1
        self.queues[priority].append(name)
        label, _ = self.LABELS[priority]
        self.status_lbl.config(
            text=f"✓ {name} ({label.split()[-1]}) ditambahkan ke antrian.")
        self.draw_row(priority)

    def serve(self):
        for p in self.PRIORITIES:
            if self.queues[p]:
                patient = self.queues[p].popleft()
                self.status_lbl.config(text=f"🏥 Melayani pasien: {patient}")
                self.draw_row(p)
                return
        self.status_lbl.config(text="⚠ Tidak ada pasien dalam antrian!")

    def reset(self):
        self.queues = {p: deque() for p in self.PRIORITIES}
        self.counter = 1
        self.draw_all()
        self.status_lbl.config(
            text="Tambahkan pasien. Pasien prioritas tinggi dilayani lebih dulu.")


# ══════════════════════════════════════════════════════════════════
#   KASUS 4: BFS GRAPH
# ══════════════════════════════════════════════════════════════════

class BFSCase:
    GRAPH = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "F"],
        "F": ["C", "E"],
    }

    def __init__(self, parent):
        self.running = False
        self.after_ids = []

        card = card_frame(parent, "BFS (Breadth-First Search)", 4)
        card.pack(fill="x", padx=20, pady=10)

        btns = tk.Frame(card, bg=BG_CARD)
        btns.pack(fill="x", padx=15, pady=5)
        make_btn(btns, "Mulai BFS dari A", self.start_bfs).pack(side="left", padx=3)
        make_btn(btns, "Reset", self.reset_bfs, color="#333a5c").pack(side="left", padx=3)

        viz = tk.Frame(card, bg="#0a0e27")
        viz.pack(fill="x", padx=15, pady=5)
        self.canvas = tk.Canvas(viz, bg="#0a0e27", height=320,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10)

        sf, self.status_lbl = make_status(card,
            'Klik "Mulai BFS" untuk melihat algoritma BFS menjelajahi graf level demi level.')
        sf.pack(fill="x", padx=15, pady=(0, 12))

        self.node_states = {n: "default" for n in self.GRAPH}
        self.edge_states = {}
        self.canvas.bind("<Configure>", lambda e: self.draw_graph())

    def get_positions(self):
        w = self.canvas.winfo_width() or 600
        cx = w // 2
        return {
            "A": (cx,      50),
            "B": (cx - 120, 150),
            "C": (cx + 120, 150),
            "D": (cx - 180, 280),
            "E": (cx - 60,  280),
            "F": (cx + 120, 280),
        }

    def draw_graph(self):
        c = self.canvas
        c.delete("all")
        pos = self.get_positions()

        # Gambar edge
        drawn = set()
        for node, neighbors in self.GRAPH.items():
            for nb in neighbors:
                key = tuple(sorted([node, nb]))
                if key in drawn:
                    continue
                drawn.add(key)
                x1, y1 = pos[node]
                x2, y2 = pos[nb]
                state = self.edge_states.get(key, "default")
                color = CYAN if state == "active" else "#1e3050"
                width = 3 if state == "active" else 2
                c.create_line(x1, y1, x2, y2, fill=color, width=width)

        # Gambar node
        R = 28
        colors = {
            "default":  (BG_CARD, CYAN),
            "visiting": (YELLOW, PINK),
            "visited":  (PURPLE, PINK),
        }
        for node, (x, y) in pos.items():
            state = self.node_states[node]
            fill, outline = colors[state]
            c.create_oval(x - R, y - R, x + R, y + R,
                          fill=fill, outline=outline, width=3)
            c.create_text(x, y, text=node, fill=WHITE,
                          font=("Courier New", 13, "bold"))

    def start_bfs(self):
        if self.running:
            return
        self.running = True
        self.node_states = {n: "default" for n in self.GRAPH}
        self.edge_states = {}
        self.draw_graph()

        visited = set(["A"])
        queue = deque(["A"])
        steps = []   # list of (node_to_visit, edges_to_activate)

        # Simulasi BFS untuk mendapat urutan langkah
        bfs_q = deque(["A"])
        vis = {"A"}
        order = []
        parent_edge = {}
        while bfs_q:
            cur = bfs_q.popleft()
            order.append(cur)
            for nb in self.GRAPH[cur]:
                if nb not in vis:
                    vis.add(nb)
                    bfs_q.append(nb)
                    parent_edge[nb] = tuple(sorted([cur, nb]))

        self._bfs_animate(order, parent_edge, 0)

    def _bfs_animate(self, order, parent_edge, step):
        if step >= len(order):
            self.status_lbl.config(text="✓ BFS selesai! Semua node telah dikunjungi.")
            self.running = False
            return

        node = order[step]
        self.status_lbl.config(text=f"🔍 Mengunjungi: {node}")
        self.node_states[node] = "visiting"
        if node in parent_edge:
            self.edge_states[parent_edge[node]] = "active"
        self.draw_graph()

        def finish_visit():
            self.node_states[node] = "visited"
            self.draw_graph()
            aid = self.canvas.after(
                400, lambda: self._bfs_animate(order, parent_edge, step + 1))
            self.after_ids.append(aid)

        aid = self.canvas.after(800, finish_visit)
        self.after_ids.append(aid)

    def reset_bfs(self):
        for aid in self.after_ids:
            self.canvas.after_cancel(aid)
        self.after_ids.clear()
        self.running = False
        self.node_states = {n: "default" for n in self.GRAPH}
        self.edge_states = {}
        self.draw_graph()
        self.status_lbl.config(
            text='Klik "Mulai BFS" untuk melihat BFS menjelajahi graf level demi level.')


# ══════════════════════════════════════════════════════════════════
#   KASUS 5: AIRPORT SIMULATION
# ══════════════════════════════════════════════════════════════════

class AirportCase:
    def __init__(self, parent):
        self.queue = deque()
        self.agents = [{"id": i + 1, "busy": False, "time_left": 0}
                       for i in range(3)]
        self.current_time = 0
        self.total_served = 0
        self.total_wait = 0
        self.running = False
        self.after_id = None
        self.passenger_counter = 1

        card = card_frame(parent, "Simulasi Loket Tiket Bandara", 5)
        card.pack(fill="x", padx=20, pady=10)

        btns = tk.Frame(card, bg=BG_CARD)
        btns.pack(fill="x", padx=15, pady=5)
        make_btn(btns, "Mulai Simulasi", self.start).pack(side="left", padx=3)
        make_btn(btns, "Pause",          self.pause).pack(side="left", padx=3)
        make_btn(btns, "Reset",          self.reset, color="#333a5c").pack(side="left", padx=3)

        viz = tk.Frame(card, bg="#0a0e27", pady=10)
        viz.pack(fill="x", padx=15, pady=5)

        # Stats grid
        stats_frame = tk.Frame(viz, bg="#0a0e27")
        stats_frame.pack(fill="x", padx=10, pady=5)
        self.stat_vars = {}
        stat_defs = [
            ("queue_size", "Penumpang dalam Antrian", "0"),
            ("served",     "Total Dilayani",          "0"),
            ("avg_wait",   "Waktu Tunggu Rata-rata",  "0.0"),
            ("cur_time",   "Waktu Sekarang",          "0"),
        ]
        for col, (key, label, default) in enumerate(stat_defs):
            box = tk.Frame(stats_frame, bg="#0d1530", padx=12, pady=8,
                           highlightbackground=CYAN, highlightthickness=1)
            box.grid(row=0, column=col, padx=5, sticky="nsew")
            stats_frame.columnconfigure(col, weight=1)
            tk.Label(box, text=label, bg="#0d1530", fg=GRAY,
                     font=("Courier New", 8)).pack()
            var = tk.StringVar(value=default)
            self.stat_vars[key] = var
            tk.Label(box, textvariable=var, bg="#0d1530", fg=CYAN,
                     font=("Courier New", 18, "bold")).pack()

        # Agen
        agent_frame = tk.Frame(viz, bg="#0a0e27")
        agent_frame.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(agent_frame, text="Agen Loket:", bg="#0a0e27", fg=CYAN,
                 font=("Courier New", 9, "bold")).pack(side="left", padx=5)
        self.agent_labels = []
        for _ in range(3):
            lbl = tk.Label(agent_frame, text="🟢", bg="#0a0e27",
                           font=("Courier New", 22))
            lbl.pack(side="left", padx=8)
            self.agent_labels.append(lbl)

        # Antrian penumpang
        q_frame = tk.Frame(viz, bg="#0a0e27")
        q_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(q_frame, text="Antrian Penumpang:", bg="#0a0e27", fg=CYAN,
                 font=("Courier New", 9, "bold")).pack(side="left", padx=5)
        self.queue_canvas = tk.Canvas(q_frame, bg="#0a0e27", height=50,
                                      highlightthickness=0)
        self.queue_canvas.pack(side="left", fill="x", expand=True, padx=5)

        sf, self.status_lbl = make_status(card,
            "Simulasi discrete event dengan 3 agen loket. Penumpang datang secara random dan dilayani FIFO.")
        sf.pack(fill="x", padx=15, pady=(0, 12))

        self.render()

    def render(self):
        # Stats
        self.stat_vars["queue_size"].set(str(len(self.queue)))
        self.stat_vars["served"].set(str(self.total_served))
        avg = f"{(self.total_wait / self.total_served):.1f}" if self.total_served else "0.0"
        self.stat_vars["avg_wait"].set(avg)
        self.stat_vars["cur_time"].set(str(self.current_time))

        # Agen
        for i, agent in enumerate(self.agents):
            self.agent_labels[i].config(text="🔴" if agent["busy"] else "🟢")

        # Antrian penumpang
        c = self.queue_canvas
        c.delete("all")
        items = list(self.queue)
        if not items:
            c.create_text(80, 25, text="Kosong", fill=GRAY,
                          font=("Courier New", 10))
        else:
            bw = 52
            for i, p in enumerate(items[:12]):  # max tampil 12
                x = 5 + i * (bw + 8)
                c.create_rectangle(x, 5, x + bw, 45,
                                   fill=PURPLE, outline=CYAN, width=1)
                c.create_text(x + bw // 2, 25, text=f"P{p['id']}",
                              fill=WHITE, font=("Courier New", 8, "bold"))
                if i < len(items) - 1 and i < 11:
                    c.create_text(x + bw + 4, 25, text="→",
                                  fill=YELLOW, font=("Courier New", 11))

    def tick(self):
        if not self.running:
            return
        self.current_time += 1

        # Kedatangan acak (30%)
        if random.random() < 0.3:
            self.queue.append({
                "id": self.passenger_counter,
                "arrival": self.current_time,
                "service_time": random.randint(2, 4),
            })
            self.passenger_counter += 1

        # Tugaskan ke agen bebas
        for agent in self.agents:
            if not agent["busy"] and self.queue:
                p = self.queue.popleft()
                agent["busy"] = True
                agent["time_left"] = p["service_time"]
                self.total_wait += self.current_time - p["arrival"]

        # Proses agen
        for agent in self.agents:
            if agent["busy"]:
                agent["time_left"] -= 1
                if agent["time_left"] <= 0:
                    agent["busy"] = False
                    self.total_served += 1

        self.render()

        if self.current_time >= 60:
            self.pause()
            avg = f"{(self.total_wait / self.total_served):.1f}" if self.total_served else "0"
            self.status_lbl.config(
                text=f"✓ Simulasi selesai (60 menit). Rata-rata waktu tunggu: {avg} menit.")
        else:
            self.after_id = self.queue_canvas.after(500, self.tick)

    def start(self):
        if self.running:
            return
        self.running = True
        self.tick()

    def pause(self):
        self.running = False
        if self.after_id:
            self.queue_canvas.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):
        self.pause()
        self.queue.clear()
        self.agents = [{"id": i + 1, "busy": False, "time_left": 0}
                       for i in range(3)]
        self.current_time = 0
        self.total_served = 0
        self.total_wait = 0
        self.passenger_counter = 1
        self.render()
        self.status_lbl.config(
            text="Simulasi discrete event dengan 3 agen loket. Penumpang datang secara random dan dilayani FIFO.")


# ══════════════════════════════════════════════════════════════════
#   MAIN APP
# ══════════════════════════════════════════════════════════════════

class App:
    def __init__(self, root):
        self.root = root
        root.title("Queue Visualizations – 5 Kasus Nyata")
        root.configure(bg=BG_DARK)
        root.geometry("1000x900")
        root.minsize(800, 600)

        # Header
        header = tk.Frame(root, bg=BG_DARK, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="QUEUE VISUALIZATIONS",
                 bg=BG_DARK, fg=CYAN,
                 font=("Courier New", 22, "bold")).pack()
        tk.Label(header, text="5 Implementasi Queue dalam Kasus Nyata",
                 bg=BG_DARK, fg=GRAY,
                 font=("Courier New", 10)).pack()

        # Scrollable canvas
        outer = tk.Frame(root, bg=BG_DARK)
        outer.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(outer, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(outer, bg=BG_DARK, yscrollcommand=scrollbar.set,
                                highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.inner = tk.Frame(self.canvas, bg=BG_DARK)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self.canvas.bind_all("<Button-5>",   self._on_mousewheel)

        # Buat semua kasus
        PrinterCase(self.inner)
        HotPotatoCase(self.inner)
        HospitalCase(self.inner)
        BFSCase(self.inner)
        AirportCase(self.inner)

        # Padding bawah
        tk.Frame(self.inner, bg=BG_DARK, height=30).pack()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()